import streamlit as st
import pandas as pd
import plotly.graph_objects as gr
from datetime import datetime
from predict import calculate_oil_status

# 1. 웹페이지 상단 설정 (제목 및 아이콘)
st.set_page_config(
    page_title="Engine Oil Predictor",
    page_icon="🚗",
    layout="wide"
)

# 2. 메인 타이틀 디자인
st.title("🚗 자동차 엔진오일 수명 및 화학 열화 예측 시스템")
st.markdown("---")

# 3. 화면을 왼쪽(입력창)과 오른쪽(결과창) 반반으로 분할
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📋 차량 및 운행 정보 입력")
    
    # 입력 폼 생성
    with st.form("input_form"):
        oil_type = st.selectbox(
            "🛢️ 윤활유 종류 (점도 규격)",
            ["0W-20", "5W-30", "5W-40"]
        )
        
        current_mileage = st.number_input(
            "🛣️ 최근 교체 후 현재까지 주행거리 (km)",
            min_value=0, max_value=50000, value=5000, step=500
        )
        
        last_change_date = st.date_input(
            "📅 최근 엔진오일 교체일",
            value=datetime.today()
        )
        
        driving_env = st.selectbox(
            "🚦 주요 운행 환경",
            ["고속도로 위주 (양호)", "일반 복합 주행 (보통)", "시내 중심 / 단거리 (가혹)"]
        )
        
        daily_mileage = st.number_input(
            "⏱️ 하루 평균 주행거리 (km)",
            min_value=1, max_value=500, value=30, step=5
        )
        
        # 제출 버튼
        submitted = st.form_submit_button("🔮 엔진오일 상태 예측하기")

# 4. 버튼을 누르면 오른쪽 화면에 예측 결과 출력
with col2:
    st.subheader("📊 논문 데이터 기반 분석 결과")
    
    # 사용자가 버튼을 눌렀을 때 실행되는 로직
    if submitted:
        # predict.py의 함수를 호출하여 계산 결과 받아오기
        result = calculate_oil_status(
            oil_type, current_mileage, last_change_date, daily_mileage, driving_env
        )
        
        # 4-1. 상태 및 종합 열화지수 표시
        st.metric(label="🚨 엔진오일 종합 상태", value=result["status"])
        
        # 프로그레스 바로 열화지수 시각화
        st.write(f"**종합 열화지수:** {result['degradation_index']}%")
        st.progress(result["degradation_index"] / 100)
        
        st.markdown("---")

        # 핵심 정보(교체 시기, 남은 주행거리) 대형 강조 유지
        st.subheader("📅 핵심 교체 시기 안내")
        
        st.markdown(f"### 📍 남은 주행 가능 거리: <span style='color:#00cc66; font-size:28px; font-weight:bold;'>약 {result['remaining_mileage']:,} km</span>", unsafe_allow_html=True)
        
        if isinstance(result["predicted_change_date"], datetime) or hasattr(result["predicted_change_date"], "strftime"):
            predicted_date_str = result["predicted_change_date"].strftime('%Y년 %m월 %d일')
            st.markdown(f"### 📅 예상 다음 교체 시점: <span style='color:#ff4b4b; font-size:28px; font-weight:bold;'>{predicted_date_str}</span> 전후", unsafe_allow_html=True)
        else:
            st.markdown(f"### 📅 예상 다음 교체 시점: <span style='color:#ff4b4b; font-size:28px; font-weight:bold;'>{result['predicted_change_date']}</span>", unsafe_allow_html=True)
            
        st.markdown("---")
        
        # ⭐ [수정 반영] HTML 테그를 사용하여 세부 화학 수치와 제목의 폰트 크기를 작게 축소
        st.subheader("🧪 세부 화학적 성질 변동 예측")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<p style='font-size:14px; color:gray; margin-bottom:2px;'>산화도 (Oxidation)</p><p style='font-size:20px; font-weight:bold; margin-top:0px;'>{result['oxidation']} Abs</p>", unsafe_allow_html=True)
            st.caption("💡 **산화도**: 오일이 고온 스트레스와 산소로 인해 변질된 지표 (높을수록 불리)")
        with m2:
            st.markdown(f"<p style='font-size:14px; color:gray; margin-bottom:2px;'>전산가 (TAN)</p><p style='font-size:20px; font-weight:bold; margin-top:0px;'>{result['tan']} mgKOH</p>", unsafe_allow_html=True)
            st.caption("💡 **전산가(TAN)**: 내부 산성 물질의 양. 수명이 갈수록 점차 상승 (높을수록 불리)")
        with m3:
            st.markdown(f"<p style='font-size:14px; color:gray; margin-bottom:2px;'>전염기가 (TBN)</p><p style='font-size:20px; font-weight:bold; margin-top:0px;'>{result['tbn']} mgKOH</p>", unsafe_allow_html=True)
            st.caption("💡 **전염기가(TBN)**: 산성 물질을 중화하는 엔진 보호 첨가제 잔여량 (낮을수록 위험)")
            
        st.markdown("---")
        
        # 5. Plotly를 활용한 화학적 성질 추이 그래프 그리기
        st.subheader("📈 주행거리에 따른 성질 변화 추이 추정 그래프")
        
        trends = result["trends"]
        
        fig = gr.Figure()
        
        fig.add_trace(gr.Scatter(
            x=trends["mileage"], y=trends["oxidation"],
            mode='lines+markers', name='산화도 (Oxidation)', line=dict(color='orange', width=2)
        ))
        
        fig.add_trace(gr.Scatter(
            x=trends["mileage"], y=trends["tan"],
            mode='lines+markers', name='전산가 (TAN)', line=dict(color='red', width=2)
        ))
        
        fig.add_trace(gr.Scatter(
            x=trends["mileage"], y=trends["tbn"],
            mode='lines+markers', name='전염기가 (TBN)', line=dict(color='blue', width=2)
        ))
        
        fig.add_vline(x=current_mileage, line_width=2, line_dash="dash", line_color="green")
        fig.add_annotation(x=current_mileage, y=max(trends["oxidation"]), text="현재 주행 시점", showarrow=True, arrowhead=1)

        fig.update_layout(
            xaxis_title="누적 주행거리 (km)",
            yaxis_title="수치 변화",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("💡 왼쪽 창에 정보를 입력한 후 **[엔진오일 상태 예측하기]** 버튼을 누르면 학술 논문 기반 수식 모델을 이용한 시뮬레이션 결과와 추이 그래프가 나타납니다.")
