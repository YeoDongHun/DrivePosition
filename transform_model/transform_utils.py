import math
from transform_base import *

def transformModel(setting:Drivepos, target:CarModel, personal:PersonalConst, ver) -> Drivepos:
    #####좌석시트
    A = setting.a_u + setting.model.a_d     #사용자가 편안하다고 느끼는 공간
    delta_a = A - target.a_d                #바뀐차량에서 사용자가 움직여야하는 x값

    #ver 1 : 바닥에서 편안한 공간을 확보한 값을 이용하여 시트조정
    B = setting.b_u + setting.model.b_d
    delta_b = B - target.b_d
    #ver 2 : 대시보드에서 시선이 올라오는 고정값으로 시트조정
    if ver == 2:
        B = - setting.b_u - setting.model.b_d + setting.model.e
        delta_b = - B - target.b_d + target.e
    #ver 3: 대시보드에 사용자 시선이 위치하는 지점의 비율을 고려하여 시트조정.
    elif ver == 3 :
        B = ( personal.hip_to_eye + setting.b_u + setting.model.b_d - setting.model.e ) / setting.model.g
        delta_b = B * target.g - personal.hip_to_eye - target.b_d + target.e

    #####사이드미러
    setting_C = setting.a_u + setting.model.c   # 사이드미러 중앙 ~ 시트설정후 사용자의 눈위치 (차량 옆면과 수평이 되는 거리)
    target_C = delta_a + target.c
    setting_D_left = setting.model.d_left       # 좌측 사이드미러 중앙 ~ 차량시트 중앙까지의 거리
    target_D_left = target.d_left
    setting_D_right = setting.model.d_right     # 우측 사이드미러 중앙 ~ 차량시트 중앙까지의 거리
    target_D_right = target.d_right
    setting_E = setting.b_u + setting.model.b_d + personal.hip_to_eye - setting.model.f  # 사이드미러 중앙 ~ 사용자의 눈높이 // (바닥 ~ 조정된시트의 높이) + (사람의 엉덩이 ~ 눈위치) - (바닥 ~ 미러)
    target_E = delta_b + target.b_d + personal.hip_to_eye - target.f
    
    #사이드미러 각 표준값으로 세팅 (시야가 차체 방향과 나란하게 나감.)
    p_left = 90 # 좌측사이드 좌우 시야각의 각도 (사이드미러에서 바라봤을때의 좌우시야 각) // 사용자 취향반영 (바깥쪽(>90), 중간(90), 안쪽(<90)..)
    p_right = 90 # 우측사이드 좌우 시야각의 각도 (사이드미러에서 바라봤을때의 좌우시야 각) // 사용자 취향반영 (바깥쪽(>90), 중간(90), 안쪽(<90)..)
    q = 90 # 상하 시야각의 각도 (사이드미러에서 바라봤을때의 상하시야 각) // 사용자 취향반영 (위(>90), 중간(90), 아래(<90)..)
    
    #사이드미러 각 사용자 취향고려
    if not personal.default_side:
        p_left = 2*setting.lr_angle_left - math.degrees(math.atan2(setting_C, setting_D_left))
        p_right = 2*setting.lr_angle_right - math.degrees(math.atan2(setting_C, setting_D_right))
        q = 2*setting.ud_angle + math.degrees(math.atan2(setting_C, setting_E))
    
    delta_lr_angle_left = (p_left + math.degrees(math.atan2(target_C, target_D_left)))/2    #사용자가 움직여야하는 사이드미러 좌우각도
    delta_lr_angle_right = (p_right + math.degrees(math.atan2(target_C, target_D_right)))/2 #사용자가 움직여야하는 사이드미러 좌우각도
    delta_ud_angle = (q - math.degrees(math.atan2(target_C, target_E)))/2                   #사용자가 움직여야하는 사이드미러 상하각도
    
    return Drivepos(delta_a, delta_b, delta_lr_angle_left, delta_lr_angle_right, delta_ud_angle, target)


def getToMove(setting:Drivepos, current:Drivepos) -> Drivepos:
    return Drivepos(setting.a_u - current.a_u, setting.b_u - current.b_u, setting.lr_angle_left - current.lr_angle_left, setting.lr_angle_right - current.lr_angle_left , setting.ud_angle - current.ud_angle, setting.model)

'''/*
****예시 상황****
   모닝에서 DrivePosition을 저장한 사용자가 그랜저를 운전하려는 상황
   이전에 한번 등록한 차량 세팅값을 이용하여 새로운 차량에서 사용자 맞춤 세팅값을 적용.
*/'''
'''/*
****IO Description****
   -input-
   
   <차량재원> : CarModel
    페달 ~ 시트를 맨앞으로 당겼을때의 거리
    차량내부 바닥 ~ 시트를 맨아래로 내렸을때의 거리
    사이드미러 중앙 ~ 시트를 맨앞으로 당겼을때 눈위치(사람머리두께를 약 17 ~ 18cm 라고 가정, 차량 옆면과 수평이 되는 거리측정.)
    좌측 사이드미러 중앙 ~ 시트 중앙까지의 거리 (차량 옆면과 수직되는 거리측정.)
    우측 사이드미러 중앙 ~ 시트 중앙까지의 거리 (차량 옆면과 수직되는 거리측정.)
    차량내부 바닥 ~ 대시보드
    차량내부 바닥 ~ 사이드미러 중앙까지의 높이
    대시 ~ 천장
   
   <사용자 특성값> : PersonalConst
    사용자가 앉았을때 엉덩이 ~ 눈높이 << 사용자의 키입력으로 부터 받아옴. => 이후 카메라 센서를 이용하여 측정을 자동화 하는 방법이 있음.
   
   <사용자 세팅값> : Drivepos
    초기 차량에서 조정한 시트와 사이드미러의 조정값.
    
   -process-
   1. input값을 토대로 사용자 특성을 추출
    시트x축 : 사용자의 편안한 공간 확보
    시트y축 : 
     / ver 1 : 바닥에서 편안한 공간을 확보한 값을 이용하여 시트조정
     / ver 2 : 대시보드에서 시선이 올라오는 고정값으로 시트조정 
     / ver 3: 대시보드에 사용자 시선이 위치하는 지점의 비율을 고려하여 시트조정.
    사이드미러 좌우,상하 : 
     / 사용자가 미러를 바라봤을때 보이는 시야의 방향을 고려하여 각도 조절. (즉, 사이드 미러에서 반사된 사용자의 시야각)
     / default : 시야각을 90도. 즉, 거울을 정면에서 바라봤을 때 보이는 장면을 볼 수 있게 설정.
   2. 추출된 사용자 특성을 토대로 새로운 차량에 적용.
   3. 새로운 차량에 적용되있던 포지션에서 1,2 에서 구한 포지션을 적용.
   
   -output-
   1. 새로운 차에서의 개인 포지션
   2. 움직일 값
*/'''
def main():
    #차종별 상수 세팅
    Morning = CarModel(34, 30, 63.5, 50.5, 103.5, 77, 77, 35, "Morning") # 가상의 값 (6, 7 ,8)
    Avante = CarModel(34, 30, 74, 55, 125, 77, 77, 38,"Avante") # 가상의 값 (2, 8)
    Genesis_G70 = CarModel(34, 29, 51, 57, 134, 77, 80, 40, "Genesis_G70") # 현재 제네시스만 정확.

    #{ x축 조정값, y축조정값, 사이드미러 좌측 조정값, 사이드미러 우측 조정값, 사이드미러 상하 조정값, 차량모델 }*/
    setting_Model= Drivepos(4, 5, 50, 48, 35, Morning)
    current_Model_setting = Drivepos(1, 2, 0, 0, 0, Avante)
    
    hip_to_eye=0.0 # 엉덩이 ~ 시야까지의 거리.(키로 부터 일정한 비율로 받아옴)
    default_setting = 0 # 사용자취향x 표준값 적용.(선택사항)
    ver=0 # ver 2 : 대시보드에서 시선이 올라오는 고정값으로 시트조정 // ver 3: 대시보드에 사용자 시선이 위치하는 지점의 비율을 고려하여 시트조정.

    # 엉덩이에서 눈높이 까지의 길이
    hip_to_eye = float(input("Enter your height : "))# 키입력
    hip_to_eye = hip_to_eye * 0.438 + 5.0973 # 키와 엉덩이에서 눈높이까지의 길이에 대한 연관관계
    print("\n")
    #//입력 모델의 세팅 출력
    print("** setting Model : {} **".format(setting_Model.model.name))
    print("x : {}".format(setting_Model.a_u))
    print("y : {}".format(setting_Model.b_u))
    print("lr_angle_left : {}".format(setting_Model.lr_angle_left))
    print("lr_angle_right : {}".format(setting_Model.lr_angle_right))
    print("ud_angle : {}".format(setting_Model.ud_angle))
    print("\n")

    #//현재 차량 모델에 따라 변환된 세팅값 출력
    
    while(True):
        ver = int(input("choose height version (1 or 2 or 3): "))
        if ver==1 or ver==2 or ver==3:
            break
        else:
            print("plz check you had entered..")

    while(True):
        default_setting = int(input("Do you want default setting?? (YES:1 NO:0): "))
        if default_setting==0 or default_setting==1:
            break
        else:
            print("plz check you had entered..")
    print("\n")
    get_transformed_setting = transformModel(setting_Model, Avante, PersonalConst(hip_to_eye, default_setting), ver)

    print("** setting Model : Avante(transformed) **")
    print("x : {}".format(get_transformed_setting.a_u))
    print("y : {}".format(get_transformed_setting.b_u))
    print("lr_angle_left : {}".format(get_transformed_setting.lr_angle_left))
    print("lr_angle_left : {}".format(get_transformed_setting.lr_angle_right))
    print("ud_angle : {}".format(get_transformed_setting.ud_angle))
    print("model name : {}".format(get_transformed_setting.model.name))
    print("\n")

    #새로운 차량의 현재 세팅값 출력
    print("** current setting : {} **".format(current_Model_setting.model.name))
    print("x : {}".format(current_Model_setting.a_u))
    print("y : {}".format(current_Model_setting.b_u))
    print("lr_angle_left : {}".format(current_Model_setting.lr_angle_left))
    print("lr_angle_left : {}".format(current_Model_setting.lr_angle_right))
    print("ud_angle : {}".format(current_Model_setting.ud_angle))
    print("\n")

    #얼마나 움직여야 하는지 출력
    toMove = getToMove(get_transformed_setting, current_Model_setting)
    print("to move\nx {}\ny {}\nlr_angle_left {}\nlr_angle_right {}\nud_angle {}\n".format(toMove.a_u, toMove.b_u, toMove.lr_angle_left, toMove.lr_angle_right, toMove.ud_angle))

if __name__=='__main__':
    main()