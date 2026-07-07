import numpy as np
from datetime import timedelta
from oil_database import oil_database

def calculate_oil_status(oil_type, current_mileage, last_change_date, daily_mileage, driving_env):
    """
    주행거리와 운행환경을 바탕으로 엔진오일의 화학적 열화 상태를 예측하는 함수
    """
    # 1. 오일 기본 데이터 가져오기
    spec = oil_database.get(oil_type, oil_database["5W-30"])
    max_life = spec["life"]
    init_tbn = spec["initial_tbn"]
    init_tan = spec["initial_tan"]
    
    # 2. 운행 환경에 따른 가중치 (시내주행이 많을수록 열화가 빨라짐)
    env_multipliers = {
        "고속도로 위주 (양호)": 0.8,
        "일반 복합 주행 (보통)": 1.0,
        "시내 중심 / 단거리 (가혹)": 1.3
    }
    multiplier = env_multipliers.get(driving_env, 1.0)
    
    # 3. 실질 체감 주행거리 계산 (가중치 반영)
    effective_mileage = current_mileage * multiplier
    
    # 4. 논문 데이터 기반 화학적 수치 시뮬레이션 (선형 및 지수 변화 모델)
    # 주행거리가 늘어날수록 산화도와 TAN은 올라가고, TBN은 떨어집니다.
    progress = min(effective_mileage / max_life, 1.2) # 최대 120%까지 열화 표현
    
    oxidation = progress * 25.0 * multiplier # 산화도 수치
    tan = init_tan + (progress * 2.5 * multiplier) # TAN은 상승
    tbn = max(init_tbn - (progress * 5.0 * multiplier), 1.0) # TBN은 하강 (최저 1.0)
    
    # 5. 종합 열화지수 계산 (0 ~ 100%)
    degradation_index = min(int(progress * 100), 100)
    
    # 6. 상태 판정
    if degradation_index < 60 and tbn > 3.0:
        status = "🟢 양호 (안심하고 주행하셔도 좋습니다)"
    elif degradation_index < 85 and tbn > 2.0:
        status = "🟡 주의 (조만간 교체 준비가 필요합니다)"
    else:
        status = "🔴 교체 필요 (엔진 보호를 위해 즉시 교체하세요)"
        
    # 7. 남은 거리 및 예상 교체일 계산
    remaining_mileage = max(int(max_life - effective_mileage), 0)
    
    if daily_mileage > 0:
        days_left = remaining_mileage / daily_mileage
        predicted_change_date = last_change_date + timedelta(days=int(days_left))
    else:
        predicted_change_date = "일일 주행거리를 입력해주세요"
        
    # 그래프를 그리기 위한 가상의 누적 데이터 생성 (0부터 현재 주행거리까지의 추이)
    mileage_steps = np.linspace(0, max(current_mileage, max_life), 20)
    oxidation_trend = (mileage_steps * multiplier / max_life) * 25.0 * multiplier
    tan_trend = init_tan + ((mileage_steps * multiplier / max_life) * 2.5 * multiplier)
    tbn_trend = np.maximum(init_tbn - ((mileage_steps * multiplier / max_life) * 5.0 * multiplier), 1.0)

    return {
        "status": status,
        "oxidation": round(oxidation, 2),
        "tan": round(tan, 2),
        "tbn": round(tbn, 2),
        "degradation_index": degradation_index,
        "remaining_mileage": remaining_mileage,
        "predicted_change_date": predicted_change_date,
        "trends": {
            "mileage": mileage_steps.tolist(),
            "oxidation": oxidation_trend.tolist(),
            "tan": tan_trend.tolist(),
            "tbn": tbn_trend.tolist()
        }
    }