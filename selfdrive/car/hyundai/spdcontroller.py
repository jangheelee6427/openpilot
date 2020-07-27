import math
import numpy as np

from cereal import log
import cereal.messaging as messaging


from cereal import log
import cereal.messaging as messaging
from selfdrive.config import Conversions as CV
from selfdrive.controls.lib.planner import calc_cruise_accel_limits
from selfdrive.controls.lib.speed_smoother import speed_smoother
from selfdrive.controls.lib.long_mpc import LongitudinalMpc


from selfdrive.car.hyundai.values import Buttons, SteerLimitParams
from common.numpy_fast import clip, interp

from selfdrive.config import RADAR_TO_CAMERA


import common.log as trace1
import common.CTime1000 as tm
import common.MoveAvg as moveavg1

from selfdrive.kegman_conf import kegman_conf


kegman = kegman_conf()

cv_Raio = float(kegman.conf['cV_Ratio']) # 0.7
cv_Dist = float(kegman.conf['cV_Dist']) # -5

MAX_SPEED = 255.0

LON_MPC_STEP = 0.2  # first step is 0.2s
MAX_SPEED_ERROR = 2.0
AWARENESS_DECEL = -0.2     # car smoothly decel at .2m/s^2 when user is distracted

# lookup tables VS speed to determine min and max accels in cruise
# make sure these accelerations are smaller than mpc limits
_A_CRUISE_MIN_V = [-1.0, -.8, -.67, -.5, -.30]
_A_CRUISE_MIN_BP = [0., 5.,  10., 20.,  40.]

# need fast accel at very low speed for stop and go
# make sure these accelerations are smaller than mpc limits
_A_CRUISE_MAX_V = [1.2, 1.2, 0.65, .4]
_A_CRUISE_MAX_V_FOLLOWING = [1.6, 1.6, 0.65, .4]
_A_CRUISE_MAX_BP = [0.,  6.4, 22.5, 40.]

# Lookup table for turns
_A_TOTAL_MAX_V = [1.7, 3.2]
_A_TOTAL_MAX_BP = [20., 40.]

# 75th percentile
SPEED_PERCENTILE_IDX = 7

def limit_accel_in_turns(v_ego, angle_steers, a_target, steerRatio, wheelbase):
    """
    This function returns a limited long acceleration allowed, depending on the existing lateral acceleration
    this should avoid accelerating when losing the target in turns
    """

    a_total_max = interp(v_ego, _A_TOTAL_MAX_BP, _A_TOTAL_MAX_V)
    a_y = v_ego**2 * angle_steers * CV.DEG_TO_RAD / (steerRatio * wheelbase)
    a_x_allowed = math.sqrt(max(a_total_max**2 - a_y**2, 0.))

    return [a_target[0], min(a_target[1], a_x_allowed)]


class SpdController():
    def __init__(self):
        self.long_control_state = 0  # initialized to off

        self.seq_step_debug = 0
        self.long_curv_timer = 0

        self.path_x = np.arange(192)

        self.traceSC = trace1.Loger("SPD_CTRL")

        self.wheelbase = 2.845
        self.steerRatio = 12.5  # 12.5

        self.v_model = 0
        self.a_model = 0
        self.v_cruise = 0
        self.a_cruise = 0

        self.l_poly = []
        self.r_poly = []

        self.movAvg = moveavg1.MoveAvg()
        self.Timer1 = tm.CTime1000("SPD")
        self.time_no_lean = 0

        self.SC = trace1.Loger("spd")

    def reset(self):
        self.v_model = 0
        self.a_model = 0
        self.v_cruise = 0
        self.a_cruise = 0

    def calc_va(self, sm, v_ego):
        md = sm['model']
        if len(md.path.poly):
            path = list(md.path.poly)

            self.l_poly = np.array(md.leftLane.poly)
            self.r_poly = np.array(md.rightLane.poly)
            self.p_poly = np.array(md.path.poly)

            # Curvature of polynomial https://en.wikipedia.org/wiki/Curvature#Curvature_of_the_graph_of_a_function
            # y = a x^3 + b x^2 + c x + d, y' = 3 a x^2 + 2 b x + c, y'' = 6 a x + 2 b
            # k = y'' / (1 + y'^2)^1.5
            # TODO: compute max speed without using a list of points and without numpy
            y_p = 3 * path[0] * self.path_x**2 + \
                2 * path[1] * self.path_x + path[2]
            y_pp = 6 * path[0] * self.path_x + 2 * path[1]
            curv = y_pp / (1. + y_p**2)**1.5

            a_y_max = 2.975 - v_ego * 0.0375  # ~1.85 @ 75mph, ~2.6 @ 25mph
            v_curvature = np.sqrt(a_y_max / np.clip(np.abs(curv), 1e-4, None))
            model_sum = np.sum(curv, 0)
            model_speed = np.min(v_curvature)
            # Don't slow down below 20mph
            model_speed = max(30.0 * CV.MPH_TO_MS, model_speed)

            model_speed = model_speed * CV.MS_TO_KPH
            if model_speed > MAX_SPEED:
                model_speed = MAX_SPEED
        else:
            model_speed = MAX_SPEED
            model_sum = 0

        model_speed = self.movAvg.get_min(model_speed, 10)

        return model_speed, model_sum

    def get_lead(self, sm, CS):
        lead_msg = sm['model'].lead
        if lead_msg.prob > 0.5:
            dRel = float(lead_msg.dist - RADAR_TO_CAMERA)
            yRel = float(lead_msg.relY)
            vRel = float(lead_msg.relVel)
            vLead = float(CS.v_ego + lead_msg.relVel)
        else:
            dRel = 150
            yRel = 0
            vRel = 0

        return dRel, yRel, vRel

    def get_tm_speed(self, CS, set_time, add_val, safety_dis=5):
        time = int(set_time)
        
        #로직상 delta_speed는 0 또는 -1 1 차이 수준 밖에 예상 안됨
        delta_speed = CS.VSetDis - CS.clu_Vanz


        #set_speed = int(CS.VSetDis) + add_val
        #ver4
        set_speed = int(CS.clu_Vanz) + add_val
        
        if add_val > 0:  # 증가
            if delta_speed > safety_dis:
                time = 100
        else:
            if delta_speed < -safety_dis:
                time = 100

        return time, set_speed

    def update_lead(self, CS,  dRel, yRel, vRel):
        lead_set_speed = CS.cruise_set_speed_kph
        lead_wait_cmd = 300
        self.seq_step_debug = 0

        # 모드 2 또는 3이 아니라면 차간거리 속도 반영 안함
        if int(CS.cruise_set_mode) not in [2, 3]:
            return lead_wait_cmd, lead_set_speed

        self.seq_step_debug = 1
        
        #vision model 인식 거리 전달
        #dRel, yRel, vRel = self.get_lead( sm, CS )
        #if CS.lead_distance < 150:
        #    dRel = CS.lead_distance
        #    vRel = CS.lead_objspd

        dst_lead_distance = (CS.clu_Vanz*cv_Raio)   # 유지 거리.
        
        # 비율 0.6
        # 시속 50km/h 이하이면 유지거리 30m
        # 시속 60km/h 이상이면 유지거리 36m
        # 시속 80km/h 이상이면 유지거리 42m

        if dst_lead_distance < 30:
            dst_lead_distance = 30
        #elif dst_lead_distance < 50:
        #    dst_lead_distance = 50
              
        #d_delta 50
        if dRel < 150:
            self.time_no_lean = 0
            d_delta = dRel - dst_lead_distance
            lead_objspd = vRel  # 선행차량 상대속도.
        else:
            d_delta = 0
            lead_objspd = 0

        # 가속이후 속도 설정.
        if CS.driverAcc_time:
          lead_set_speed = CS.clu_Vanz
          lead_wait_cmd = 100
          self.seq_step_debug = 2
        elif CS.VSetDis >= 80 and lead_objspd < -30:
            self.seq_step_debug = 3
            lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 15, -10) #-5)  
        elif CS.VSetDis >= 70 and lead_objspd < -20:
            self.seq_step_debug = 31
            lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 15, -8) #-4)  
        elif CS.VSetDis >= 60 and lead_objspd < -15:
            self.seq_step_debug = 4
            lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 15, -6) #-3)    


        # 1. 거리 유지.
        # 차량이 가까워진다면
        
        elif d_delta < 0:
            # 선행 차량이 가까이 있으면.

            #사용안됨
            dVanz = dRel - CS.clu_Vanz


            self.seq_step_debug = 5
            #앞차가 더 빠름
            if lead_objspd >= 0:    # 속도 유지 시점 결정.
                

                self.seq_step_debug = 6
                #현재속도보다 설정속도가 20 이상 높다면 크루즈 감속 진행
                #투싼은 CS.VSetDis = CS.clu_vanz 이기 때문에 아래 if 의미없음
                #무조건 else
                if CS.VSetDis > (CS.clu_Vanz + 20):
                    self.seq_step_debug = 61
                    lead_wait_cmd = 200
                    lead_set_speed = CS.VSetDis - 1  # CS.clu_Vanz + 5
                    if lead_set_speed < 40:
                        lead_set_speed = 30 #40
                
                #현 속도 유지
                else:
                    self.seq_step_debug = 62
                    lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 100, 0)                    
                    
            #내차가 더 빠름        
            elif lead_objspd < -30 or (dRel < 60 and CS.clu_Vanz > 60 and lead_objspd < -5):            
                self.seq_step_debug = 7
                lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 15, -6) #-3)
            elif lead_objspd < -20 or (dRel < 80 and CS.clu_Vanz > 80 and lead_objspd < -5):            
                self.seq_step_debug = 8
                lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 20, -4) #-2)
            elif lead_objspd < -10:
                self.seq_step_debug = 9
                lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 50, -2) #-1)
            #내차 속도가 빨라지기 시작하는 시점
            elif lead_objspd < 0:
                self.seq_step_debug = 10
                lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 80, -2) #-1)
            
            #선행 차량이 유지거리보다 가까이 있다면 가속 하지 않음
            #else:
            #    self.seq_step_debug = 11
            #    lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 50, 1)

        # 선행차량이 멀리 있으면.
        elif lead_objspd < -30 and dRel < 70:  #거리 조건 추가
            #빠르게 가까워지며 상대거리가 50m 이하이면 속도 빨리 줄임
            self.seq_step_debug = 12
            lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 15, -4) #-2)
        elif lead_objspd < -20 and dRel < 50:  #거리 조건 추가
            #빠르게 가까워지며 상대거리가 50m 이하이면 속도 빨리 줄임
            self.seq_step_debug = 12
            lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 15, -4) #-2)
        
        #기준을 30으로잡았기 때문에 아래 코드 무시됨
        elif lead_objspd < -10 and dRel < 30:  #거리 조건 추가:
            self.seq_step_debug = 13
            lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 15, -2) #-1)
        
        #선행차량은 멀리 있지만 차량이 상대속도가 -5km/h 차이라면 가까워지고 있으므로
        # 천천히 속도를 줄임
        elif lead_objspd < -5:
            self.seq_step_debug = 14
            lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 150, -2) #-1)

        #앞차가 멀리있으며, 
        #크루즈 설정 속도보다 현 차속이 느리면서
        # 목표 60 / 내차 30
        elif CS.cruise_set_speed_kph > CS.clu_Vanz:
            self.seq_step_debug = 16
            # 선행 차량이 가속하고 있으면.
            if dRel >= 150:
                self.seq_step_debug = 17
                lead_wait_cmd, lead_set_speed = self.get_tm_speed( CS, 100, 1) #3 )

            #선행차량 가속중이지만 상대속도가 -5보다 적다면
            elif lead_objspd < cv_Dist:
                self.seq_step_debug = 18
                #lead_set_speed = int(CS.VSetDis)
                lead_set_speed = int(CS.cruise_set_speed_kph)
                lead_wait_cmd =100
            elif lead_objspd < 5:
                self.seq_step_debug = 20
                lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 100, 1) #1)
            elif lead_objspd < 10:
                self.seq_step_debug = 21
                lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 100, 1) #2)
            elif lead_objspd < 30:
                self.seq_step_debug = 22
                lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 100, 1) #3)                
            else:
                self.seq_step_debug = 23
                lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 100, 1) #5)

        return lead_wait_cmd, lead_set_speed

    def update_lead2(self, CS,  dRel, yRel, vRel):
        lead_set_speed = CS.cruise_set_speed_kph
        lead_wait_cmd = 600
        self.seq_step_debug = 0

																			 
        if int(CS.cruise_set_mode) not in [2, 3]:
            return lead_wait_cmd, lead_set_speed

        self.seq_step_debug = 1
		
										  
        #dRel, yRel, vRel = self.get_lead( sm, CS )
        #if CS.lead_distance < 150:
        #    dRel = CS.lead_distance
        #    vRel = CS.lead_objspd

        dst_lead_distance = (CS.clu_Vanz*cv_Raio)   # 유지 거리.

        #if dst_lead_distance > 100:
        #    dst_lead_distance = 100
        #elif dst_lead_distance < 50:
        #    dst_lead_distance = 50
 
        if dst_lead_distance < 30:
            dst_lead_distance = 30							 


        if dRel < 150:
            self.time_no_lean = 0
            d_delta = dRel - dst_lead_distance
            lead_objspd = vRel  # 선행차량 상대속도.
        else:
            d_delta = 0
            lead_objspd = 0

        # 가속이후 속도 설정.
        if CS.driverAcc_time:
          lead_set_speed = CS.clu_Vanz
          lead_wait_cmd = 100
          self.seq_step_debug = 2
        elif CS.VSetDis > 70 and lead_objspd < -20:
            self.seq_step_debug = 3
            lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 15, -6) #-2)
        elif CS.VSetDis > 60 and lead_objspd < -15:
            self.seq_step_debug = 4
            lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 15, -6) #-2)     

        # 1. 거리 유지.
 
        elif d_delta < 0:
            # 선행 차량이 가까이 있으면.
            dVanz = dRel - CS.clu_Vanz

            self.seq_step_debug = 5
																  
            if lead_objspd >= 0:    # 속도 유지 시점 결정.
                self.seq_step_debug = 6
                if CS.VSetDis > (CS.clu_Vanz + 10):
                    lead_wait_cmd = 200
                    lead_set_speed = CS.VSetDis - 1  # CS.clu_Vanz + 5
                    if lead_set_speed < 40:
                        lead_set_speed = 30 #30
                else:
                    lead_set_speed = int(CS.VSetDis)
																			
            elif lead_objspd < -30 or (dRel < 50 and CS.VSetDis > 60 and lead_objspd < -5):
                self.seq_step_debug = 7
                lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 15, -6) #-2)
            elif lead_objspd < -20 or (dRel < 70 and CS.VSetDis > 60 and lead_objspd < -5):
                self.seq_step_debug = 8
                lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 20, -6) #-2)
            elif lead_objspd < -10:
                self.seq_step_debug = 9
                lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 50, -3) #-1)
            elif lead_objspd < 0:
                self.seq_step_debug = 10
                lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 80, -3) #-1)
            else:
                self.seq_step_debug = 11
                lead_set_speed = int(CS.VSetDis)

        # 선행차량이 멀리 있으면.
        elif lead_objspd < -20:
									
            self.seq_step_debug = 12
            lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 15, -6) #-2)
        elif lead_objspd < -10:
            self.seq_step_debug = 13
            lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 50, -3) #-1)
        elif lead_objspd < -5:
            self.seq_step_debug = 14
            lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 150, -3) #-1)
        elif lead_objspd < -1:
            self.seq_step_debug = 15
            lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 200, -3) #-1)
												   
        elif CS.cruise_set_speed_kph > CS.clu_Vanz:
            self.seq_step_debug = 16
            # 선행 차량이 가속하고 있으면.
            if dRel >= 150:
                self.seq_step_debug = 17
                lead_wait_cmd, lead_set_speed = self.get_tm_speed( CS, 200, 3) #1)
																			   
									   
            elif lead_objspd < cv_Dist:
                self.seq_step_debug = 18
                lead_set_speed = int(CS.VSetDis)
            elif lead_objspd < 2:
                self.seq_step_debug = 19
                lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 500, 3) #1)
            elif lead_objspd < 5:
                self.seq_step_debug = 20
                lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 300, 3) #1)
            elif lead_objspd < 10:
                self.seq_step_debug = 21
                lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 200, 3) #1)
            elif lead_objspd < 30:
                self.seq_step_debug = 22
                lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 100, 3)# 1)                
            else:
                self.seq_step_debug = 23
                lead_wait_cmd, lead_set_speed = self.get_tm_speed(CS, 50, 3) #1)

        return lead_wait_cmd, lead_set_speed

    def update_curv(self, CS, sm, model_speed):
        wait_time_cmd = 0
        set_speed = CS.cruise_set_speed_kph

        # 2. 커브 감속.
        if CS.cruise_set_speed_kph >= 100:
            if model_speed < 50:
                set_speed = CS.cruise_set_speed_kph - 40 #20 
                wait_time_cmd = 100
            elif model_speed < 70:  
                set_speed = CS.cruise_set_speed_kph - 20 #10 
                wait_time_cmd = 100
            elif model_speed < 90:  
                set_speed = CS.cruise_set_speed_kph - 6 #3  
                wait_time_cmd = 150
            elif model_speed < 130:  
                set_speed = CS.cruise_set_speed_kph - 2 #1 
                wait_time_cmd = 200
            if set_speed > model_speed:
                set_speed = model_speed
        elif CS.cruise_set_speed_kph >= 80:
            if model_speed < 70:  
                set_speed = CS.cruise_set_speed_kph - 10 #5 
                wait_time_cmd = 100
            elif model_speed < 80:  
                set_speed = CS.cruise_set_speed_kph - 4 #2 
                wait_time_cmd = 150
                if set_speed > model_speed:
                   set_speed = model_speed
        elif CS.cruise_set_speed_kph >= 60:
            if model_speed < 50: 
                set_speed = CS.cruise_set_speed_kph - 6 #3 
                wait_time_cmd = 100
            elif model_speed < 70:  
                set_speed = CS.cruise_set_speed_kph - 2 #1 
                wait_time_cmd = 150
                if set_speed > model_speed:
                   set_speed = model_speed

        return wait_time_cmd, set_speed

    def update(self, v_ego_kph, CS, sm, actuators, dRel, yRel, vRel, model_speed):
        btn_type = Buttons.NONE
        #lead_1 = sm['radarState'].leadOne
        long_wait_cmd = 500
        set_speed = CS.cruise_set_speed_kph
        dec_step_cmd = 0
        
        #ver4
        set_speed_diff = set_speed - CS.VSetDis

        if self.long_curv_timer < 600:
            self.long_curv_timer += 1


        # 선행 차량 거리유지
        lead_wait_cmd, lead_set_speed = self.update_lead2( CS,  dRel, yRel, vRel)  
        # 커브 감속.
        curv_wait_cmd, curv_set_speed = self.update_curv(CS, sm, model_speed)

        #TEST 커브 속도 반영 제외
        #curv_wait_cmd = 0

        if curv_wait_cmd != 0:
            if lead_set_speed > curv_set_speed:
                dec_step_cmd = 1
                set_speed = curv_set_speed
                long_wait_cmd = curv_wait_cmd
            else:
                set_speed = lead_set_speed
                long_wait_cmd = lead_wait_cmd
        else:
            set_speed = lead_set_speed
            long_wait_cmd = lead_wait_cmd

        

        if set_speed > CS.cruise_set_speed_kph:
            set_speed = CS.cruise_set_speed_kph
        elif set_speed < 30:
            set_speed = 30

        # control process
        target_set_speed = set_speed
        delta = int(set_speed) - int(CS.VSetDis)
        if dec_step_cmd == 0 and delta < -1:
            if delta < -3:
                dec_step_cmd = 4
            elif  delta < -2:
                dec_step_cmd = 3
            else:
                dec_step_cmd = 2
        else:
            dec_step_cmd = 1

        if self.long_curv_timer < long_wait_cmd:
            #타이머 시간동안 작동 안함
            pass
        elif CS.driverOverride == 1:  # 가속패달에 의한 속도 설정.
            if CS.cruise_set_speed_kph > CS.clu_Vanz:
                delta = int(CS.clu_Vanz) - int(CS.VSetDis)
                if delta > 1:
                    set_speed = CS.clu_Vanz               
                    self.seq_step_debug = 97
                    btn_type = Buttons.SET_DECEL
            self.long_curv_timer = 0
        elif delta <= -2:
            set_speed = CS.VSetDis - dec_step_cmd
            self.seq_step_debug = 98   
            btn_type = Buttons.SET_DECEL
            self.long_curv_timer = 0
        elif delta >= 2 and (model_speed > 200 or CS.clu_Vanz < 200):
            set_speed = CS.VSetDis + dec_step_cmd
            self.seq_step_debug = 99
            btn_type = Buttons.RES_ACCEL
            self.long_curv_timer = 0            
            if set_speed > CS.cruise_set_speed_kph:
                set_speed = CS.cruise_set_speed_kph
        else:
            if self.long_curv_timer > long_wait_cmd:
                CS.cruise_set_speed_kph = set_speed
            self.long_curv_timer = 0

        CS.VSetDis = CS.clu_Vanz

        if CS.cruise_set_mode == 0:
            btn_type = Buttons.NONE

        str3 = 'SS={:03.0f}/{:03.0f} SSD={:03.0f} VSD={:03.0f} pVSD={:03.0f} DAt={:03.0f}/{:03.0f}/{:03.0f} '.format(
            set_speed, long_wait_cmd, set_speed_diff, CS.VSetDis, CS.prev_VSetDis,  CS.driverAcc_time, self.long_curv_timer, long_wait_cmd  )
        str4 = ' LD/LS={:03.0f}/{:03.0f} '.format(  dRel, vRel )

        str5 = str3 +  str4
        trace1.printf2( str5 )

        return btn_type, set_speed