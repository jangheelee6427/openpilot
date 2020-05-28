# This Python file uses the following encoding: utf-8
# -*- coding: utf-8 -*-
from cereal import car, log

# Priority
class Priority:
  LOWEST = 0
  LOWER = 1
  LOW = 2
  MID = 3
  HIGH = 4
  HIGHEST = 5

AlertSize = log.ControlsState.AlertSize
AlertStatus = log.ControlsState.AlertStatus
AudibleAlert = car.CarControl.HUDControl.AudibleAlert
VisualAlert = car.CarControl.HUDControl.VisualAlert

class Alert():
  def __init__(self,
               alert_type,
               alert_text_1,
               alert_text_2,
               alert_status,
               alert_size,
               alert_priority,
               visual_alert,
               audible_alert,
               duration_sound,
               duration_hud_alert,
               duration_text,
               alert_rate=0.):

    self.alert_type = alert_type
    self.alert_text_1 = alert_text_1
    self.alert_text_2 = alert_text_2
    self.alert_status = alert_status
    self.alert_size = alert_size
    self.alert_priority = alert_priority
    self.visual_alert = visual_alert
    self.audible_alert = audible_alert

    self.duration_sound = duration_sound
    self.duration_hud_alert = duration_hud_alert
    self.duration_text = duration_text

    self.start_time = 0.
    self.alert_rate = alert_rate

    # typecheck that enums are valid on startup
    tst = car.CarControl.new_message()
    tst.hudControl.visualAlert = self.visual_alert

  def __str__(self):
    return self.alert_text_1 + "/" + self.alert_text_2 + " " + str(self.alert_priority) + "  " + str(
      self.visual_alert) + " " + str(self.audible_alert)

  def __gt__(self, alert2):
    return self.alert_priority > alert2.alert_priority


ALERTS = [
  Alert(
      "turningIndicatorOn",
      "턴 시그널 작동 중 핸들을 잡아주세요",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.HIGH, VisualAlert.none, AudibleAlert.none, 0., 0., .1),
  Alert(
      "lkasButtonOff",
      "오픈파일럿 사용을 위해 차량의 LKAS 버튼을 눌러주세요",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.HIGH, VisualAlert.none, AudibleAlert.none, 0., 0., .1),
  # Miscellaneous alerts
  Alert(
      "enable",
      "",
      "",
      AlertStatus.normal, AlertSize.none,
      Priority.MID, VisualAlert.none, AudibleAlert.chimeEngage, 2., 0., 0.),

  Alert(
      "disable",
      "",
      "",
      AlertStatus.normal, AlertSize.none,
      Priority.MID, VisualAlert.none, AudibleAlert.chimeDisengage, 2., 0., 0.),

  Alert(
      "fcw",
      "브레이크!",
      "추돌 위험",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.fcw, AudibleAlert.chimeWarningRepeat, 1., 2., 2.),

  Alert(
      "fcwStock",
      "브레이크!",
      "추돌 위험",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.fcw, AudibleAlert.none, 1., 2., 2.),  # no EON chime for stock FCW

  Alert(
      "steerSaturated",
      "핸들을 잡아주세요",
      "스티어링 토크가 높습니다",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 1., 2., 3.),

  Alert(
      "steerTempUnavailable",
      "핸들을 잡아주세요",
      "조향제어가 일시적으로 비활성화 되었습니다",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.chimeWarning1, .4, 2., 3.),

  Alert(
      "steerTempUnavailableMute",
      "핸들을 잡아주세요",
      "조향제어가 일시적으로 비활성화 되었습니다",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .2, .2, .2),

  Alert(
      "manualSteeringRequired",
      "핸들을 잡아주세요: 차선유지기능 꺼짐",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .0, .1, .1, alert_rate=0.25),

  Alert(
      "manualSteeringRequiredBlinkersOn",
      "핸들을 잡아주세요: 턴 시그널 켜짐",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .0, .1, .1, alert_rate=0.25),

  Alert(
      "preDriverDistracted",
      "도로상황에 주의를 기울이세요 : 주행 산만",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.none, .0, .1, .1, alert_rate=0.75),

  Alert(
      "promptDriverDistracted",
      "도로상황에 주의하세요",
      "주행 산만",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeRoadWarning, 3., .1, .1),

  Alert(
      "driverDistracted",
      "경고: 조향제어가 즉시 해제됩니다",
      "주행 산만",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGH, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, .1, .1),

  Alert(
      "preDriverUnresponsive",
      "핸들을 터치하세요: 모니터링 없음",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.none, .0, .1, .1, alert_rate=0.75),

  Alert(
      "promptDriverUnresponsive",
      "핸들을 터치하세요",
      "운전자 모니터링 없음",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarning2, .1, .1, .1),

  Alert(
      "driverUnresponsive",
      "경고: 조향제어가 즉시 해제됩니다",
      "운전자 모니터링 없음",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGH, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, .1, .1),

  Alert(
      "driverMonitorLowAcc",
      "운전자 얼굴 확인 중",
      "운전자 얼굴 인식이 어렵습니다",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.none, .4, 0., 1.),

  Alert(
      "geofence",
      "해제 필요",
      "지오 펜스 영역에 있지 않음",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.HIGH, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, .1, .1),

  Alert(
      "startup",
      "오픈파일럿 사용준비가 되었습니다",
      "안전운전을 위해 항상 핸들을 잡고 도로교통 상황을 주시하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOWER, VisualAlert.none, AudibleAlert.chimeReady, 4., 0., 5.),

  Alert(
      "startupMaster",
      "경고: 이 브랜치는 테스트되지 않았습니다",
      "안전운전을 위해 항상 핸들을 잡고 도로교통 상황을 주시하세요",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOWER, VisualAlert.none, AudibleAlert.none, 0., 0., 15.),

  Alert(
      "startupNoControl",
      "기록 모드(대시캠 모드)",
      "안전운전을 위해 항상 핸들을 잡고 도로교통 상황을 주시하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOWER, VisualAlert.none, AudibleAlert.none, 0., 0., 15.),

  Alert(
      "startupNoCar",
      "기록모드(지원되지 않는 차량)",
      "안전운전을 위해 항상 핸들을 잡고 도로교통 상황을 주시하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOWER, VisualAlert.none, AudibleAlert.none, 0., 0., 15.),

  Alert(
      "ethicalDilemma",
      "경고: 핸들을 즉시 잡아주세요",
      "윤리적 딜레마가 발견되었습니다",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 1., 3., 3.),

  Alert(
      "steerTempUnavailableNoEntry",
      "오픈파일럿 사용 불가",
      "조향 제어가 일시적으로 비활성화 되었습니다.",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 0., 3.),

  Alert(
      "manualRestart",
      "핸들을 잡아주세요",
      "수동으로 운전을 재개하세요",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "resumeRequired",
      "멈춤",
      "계속하려면 RES를 누르세요",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "belowSteerSpeed",
      "핸들을 잡아주세요",
      "차량속도가 낮아 조향제어가 일시적으로 비활성화 되었습니다",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.MID, VisualAlert.none, AudibleAlert.none, 0., 0.4, .3),

  Alert(
      "debugAlert",
      "DEBUG ALERT",
      "",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .1, .1, .1),
  Alert(
      "preLaneChangeLeft",
      "차선 변경을 위해 핸들을 좌측으로 살짝 돌리세요",
      "다른 차량에 주의하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .0, .1, .1, alert_rate=0.75),

  Alert(
      "preLaneChangeRight",
      "차선 변경을 위해 핸들을 우측으로 살짝 돌리세요",
      "다른 차량에 주의하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .0, .1, .1, alert_rate=0.75),

  Alert(
      "laneChange",
      "차선 변경 중",
      "다른 차량에 주의하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .0, .1, .1),
  
    Alert(
      "rightLCAbsm",
      "우측에 차량 접근 중",
      "차선 변경을 위해 잠시 대기합니다",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.MID, VisualAlert.none, AudibleAlert.none, 0., 0.4, .3),
  
  Alert(
      "leftLCAbsm",
      "좌측에 차량 접근 중",
      "차선 변경을 위해 잠시 대기합니다",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.MID, VisualAlert.none, AudibleAlert.none, 0., 0.4, .3),
  
  Alert(
      "preventLCA",
      "핸들을 잡아주세요",
      "도로 상황 불안으로 차선변경이 취소되었습니다",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGH, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .4, 3., 3.,),


  Alert(
      "posenetInvalid",
      "핸들을 잡아주세요",
      "전방 영상 인식이 불확실합니다",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.chimeViewUncertain, 3., 2., 3.),

  # Non-entry only alerts
  Alert(
      "wrongCarModeNoEntry",
      "오픈파일럿 사용 불가",
      "주 전원 꺼짐",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 0., 3.),

  Alert(
      "dataNeededNoEntry",
      "오픈파일럿 사용 불가",
      "캘리브레이션을 위한 데이터 필요, 자료를 업로드 하시고 다시 시작하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 0., 3.),

  Alert(
      "outOfSpaceNoEntry",
      "오픈파일럿 사용 불가",
      "저장 공간이 부족합니다",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 0., 3.),

  Alert(
      "pedalPressedNoEntry",
      "오픈파일럿 사용 불가",
      "브레이크 페달 밟음",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, "brakePressed", AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "speedTooLowNoEntry",
      "오픈파일럿 사용 불가",
      "차량 속도가 너무 느립니다",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "brakeHoldNoEntry",
      "오픈파일럿 사용 불가",
      "브레이크 해제 필요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "parkBrakeNoEntry",
      "오픈파일럿 사용 불가",
      "주차 브레이크 해제 필요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "lowSpeedLockoutNoEntry",
      "오픈파일럿 사용 불가",
      "크루즈 기능 오류: 다시 시작하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "lowBatteryNoEntry",
      "오픈파일럿 사용 불가",
      "배터리 부족",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "sensorDataInvalidNoEntry",
      "오픈파일럿 사용 불가",
      "EON 센서로부터 데이터를 받지 못했습니다",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "soundsUnavailableNoEntry",
      "오픈파일럿 사용 불가",
      "사운드 장치를 찾을 수 없습니다",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "tooDistractedNoEntry",
      "오픈파일럿 사용 불가",
      "과도한 운전 산만",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  # Cancellation alerts causing soft disabling
  Alert(
      "overheat",
      "오픈파일럿 사용 경고",
      "시스템이 과열되었습니다",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),

  Alert(
      "wrongGear",
      "오픈파일럿 사용 경고",
      "기어가 드라이브 상태가 아닙니다",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeGearDrive, 3., 2., 2.),

  Alert(
      "calibrationInvalid",
      "오픈파일럿 사용 경고",
      "캘리브레이션 오류: EON을 재 장착하고 다시 시작하세요",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),

  Alert(
      "calibrationIncomplete",
      "오픈파일럿 사용 경고",
      "캘리브레이션 진행 중...",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),

  Alert(
      "doorOpen",
      "오픈파일럿 사용 경고",
      "도어가 열려있습니다",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeDoorOpen, 3., 2., 2.),

  Alert(
      "seatbeltNotLatched",
      "오픈파일럿 사용 경고",
      "안전벨트 미체결",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeSeatBelt, 2., 2., 2.),

  Alert(
      "espDisabled",
      "오픈파일럿 사용 경고",
      "ESP 오프",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),

  Alert(
      "lowBattery",
      "오픈파일럿 사용 경고",
      "배터리 부족",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),

  Alert(
      "commIssue",
      "오픈파일럿 사용 경고",
      "프로세스 간 통신 오류가 있습니다",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),

  Alert(
      "radarCommIssue",
      "오픈파일럿 사용 경고",
      "레이더 통신 오류가 있습니다",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),

  Alert(
      "radarCanError",
      "오픈파일럿 사용 경고",
      "레이더 통신 오류: 차량을 다시 시작하세요",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),

  Alert(
      "radarFault",
      "오픈파일럿 사용 경고",
      "레이더 통신 오류: 차량을 다시 시작하세요",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),


  Alert(
      "lowMemory",
      "오픈파일럿 사용 경고",
      "메모리 부족: EON을 재시작 하세요",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),

  # Cancellation alerts causing immediate disabling
  Alert(
      "controlsFailed",
      "오픈파일럿 사용 경고",
      "차량 제어 불가",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 2.2, 3., 4.),

  Alert(
      "controlsMismatch",
      "오픈파일럿 사용 경고",
      "차량 제어 불가",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 2.2, 3., 4.),

  Alert(
      "canError",
      "오픈파일럿 사용 경고",
      "CAN통신 오류: 배선을 확인하세요",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 2.2, 3., 4.),

  Alert(
      "steerUnavailable",
      "오픈파일럿 사용 경고",
      "LKAS 오류: 차량을 다시 시작하세요",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 2.2, 3., 4.),

  Alert(
      "brakeUnavailable",
      "오픈파일럿 사용 경고",
      "크루즈 시스템 오류: 차량을 다시 시작하세요",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 2.2, 3., 4.),

  Alert(
      "gasUnavailable",
      "오픈파일럿 사용 경고",
      "가속페달 오류: 차량을 다시 시작하세요",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 2.2, 3., 4.),

  Alert(
      "reverseGear",
      "오픈파일럿 사용 경고",
      "기어가 후진상태에 있습니다",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 2.2, 3., 4.),

  Alert(
      "cruiseDisabled",
      "오픈파일럿 사용 경고",
      "크루즈 기능 꺼짐",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 2.2, 3., 4.),

  Alert(
      "plannerError",
      "오픈파일럿 사용 경고",
      "조향 처리에 오류가 있습니다",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 2.2, 3., 4.),

  Alert(
      "relayMalfunction",
      "TAKE CONTROL IMMEDIATELY",
      "Harness Malfunction",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 2.2, 3., 4.),


  # not loud cancellations (user is in control)
  Alert(
      "noTarget",
      "오픈파일럿 사용 불가",
      "선행 차량이 감지되지 않았습니다",
      AlertStatus.normal, AlertSize.mid,
      Priority.HIGH, VisualAlert.none, AudibleAlert.chimeDisengage, .4, 2., 3.),

  Alert(
      "speedTooLow",
      "오픈파일럿 사용 불가",
      "차량 속도가 너무 느립니다",
      AlertStatus.normal, AlertSize.mid,
      Priority.HIGH, VisualAlert.none, AudibleAlert.chimeDisengage, .4, 2., 3.),

  Alert(
      "speedTooHigh",
      "Speed Too High",
      "Slow down to resume operation",
      AlertStatus.normal, AlertSize.mid,
      Priority.HIGH, VisualAlert.none, AudibleAlert.chimeDisengage, .4, 2., 3.),

  # Cancellation alerts causing non-entry
  Alert(
      "overheatNoEntry",
      "오픈파일럿 사용 불가",
      "시스템이 과열되었습니다",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "wrongGearNoEntry",
      "오픈파일럿 사용 불가",
      "기어가 드라이브 상태가 아닙니다",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeGearDrive, 3., 2., 3.),

  Alert(
      "calibrationInvalidNoEntry",
      "오픈파일럿 사용 불가",
      "캘리브레이션 오류: EON을 재 장착하고 다시 시작하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "calibrationIncompleteNoEntry",
      "오픈파일럿 사용 일시 불가",
      "캘리브레이션 진행 중...",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "doorOpenNoEntry",
      "오픈파일럿 사용 불가",
      "도어가 열려있습니다",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeDoorOpen, 3., 2., 3.),

  Alert(
      "seatbeltNotLatchedNoEntry",
      "오픈파일럿 사용 불가",
      "안전벨트를 체결 하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeSeatBelt, 2., 2., 3.),

  Alert(
      "espDisabledNoEntry",
      "오픈파일럿 사용 불가",
      "ESP 꺼짐",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "geofenceNoEntry",
      "오픈파일럿 사용 불가",
      "지오 펜스 영역에 있지 않음",
      AlertStatus.normal, AlertSize.mid,
      Priority.MID, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "radarCanErrorNoEntry",
      "오픈파일럿 사용 불가",
      "레이더 통신 오류: 차를 다시 시작하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "radarFaultNoEntry",
      "오픈파일럿 사용 불가",
      "레이더 통신 오류: 차를 다시 시작하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "posenetInvalidNoEntry",
      "오픈파일럿 사용 불가",
      "전방 영상 인식이 불확실합니다",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "controlsFailedNoEntry",
      "오픈파일럿 사용 불가",
      "차량 제어 불가",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "canErrorNoEntry",
      "오픈파일럿 사용 불가",
      "CAN통신 오류: 배선을 다시 확인하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "steerUnavailableNoEntry",
      "오픈파일럿 사용 불가",
      "LKAS 오류: 차량을 다시 시작하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "brakeUnavailableNoEntry",
      "오픈파일럿 사용 불가",
      "크루즈 시스템 오류: 차량을 다시 시작하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "gasUnavailableNoEntry",
      "오픈파일럿 사용 불가",
      "가속페달 오류: 차량을 다시 시작하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "reverseGearNoEntry",
      "오픈파일럿 사용 불가",
      "기어가 후진상태에 있습니다",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "cruiseDisabledNoEntry",
      "오픈파일럿 사용 불가",
      "크루즈 기능 꺼짐",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "noTargetNoEntry",
      "오픈파일럿 사용 불가",
      "선행 차량이 감지되지 않았습니다",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "plannerErrorNoEntry",
      "오픈파일럿 사용 불가",
      "조향 처리에 오류가 있습니다",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "commIssueNoEntry",
      "오픈파일럿 사용 불가",
      "프로세스 간 통신 오류가 있습니다",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeDisengage, .4, 2., 3.),

  Alert(
      "radarCommIssueNoEntry",
      "오픈파일럿 사용 불가",
      "레이더 통신 오류가 있습니다",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeDisengage, .4, 2., 3.),

  Alert(
      "internetConnectivityNeededNoEntry",
      "오픈파일럿 사용 불가",
      "인터넷에 연결하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeDisengage, .4, 2., 3.),

  Alert(
      "lowMemoryNoEntry",
      "오픈파일럿 사용 불가",
      "메모리 부족: EON을 다시 시작하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeDisengage, .4, 2., 3.),

  Alert(
      "speedTooHighNoEntry",
      "Speed Too High",
      "Slow down to engage",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "relayMalfunctionNoEntry",
      "openpilot Unavailable",
      "Harness Malfunction",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  # permanent alerts
  Alert(
      "steerUnavailablePermanent",
      "LKAS 오류: 차량을 다시 시작하세요",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOWER, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "brakeUnavailablePermanent",
      "크루즈 시스템 오류: 차량을 다시 시작하세요",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOWER, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "lowSpeedLockoutPermanent",
      "크루즈 시스템 오류: 차량을 다시 시작하세요",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOWER, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "calibrationIncompletePermanent",
      "캘리브레이션 진행 중: ",
      "차량의 속도를 높이세요 > ",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "invalidGiraffeToyotaPermanent",
      "지원되지 않는 지라프 설정",
      "comma.ai/tg 참조",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOWER, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "invalidLkasSettingPermanent",
      "Stock LKAS is turned on",
      "Turn off stock LKAS to engage",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOWER, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "internetConnectivityNeededPermanent",
      "인터넷에 연결하세요",
      "활성화를 위해 업데이트를 확인해야 합니다",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOWER, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "communityFeatureDisallowedPermanent",
      "커뮤니티 기능 감지",
      "Enable Community Features in Developer Settings",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 0., 0., .2),  # LOW priority to overcome Cruise Error

  Alert(
      "sensorDataInvalidPermanent",
      "EON 센서로부터 데이터를 받지 못했습니다",
      "EON을 다시 시작하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOWER, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "soundsUnavailablePermanent",
      "사운드 장치를 찾을 수 없습니다",
      "EON을 다시 시작하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOWER, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "lowMemoryPermanent",
      "메모리 부족 심각",
      "EON을 다시 시작하세요",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOWER, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "carUnrecognizedPermanent",
      "기록 모드",
      "인식되지 않은 차량 모델",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOWER, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "relayMalfunctionPermanent",
      "Harness Malfunction",
      "Please Check Hardware",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOWER, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "vehicleModelInvalid",
      "차량 매개변수 인식 실패",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOWEST, VisualAlert.steerRequired, AudibleAlert.none, .0, .0, .1),

  Alert(
      "ldwPermanent",
      "핸들을 잡아주세요",
      "차선 이탈 감지",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.chimeLaneDeparture, 4., 2., 3.),
]
