import streamlit as st

st.set_page_config(
    page_title="Engine Oil Life Predictor",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 엔진오일 교체 시기 예측 시스템")

st.write("""
이 프로그램은 논문 데이터를 기반으로
엔진오일의 열화 상태를 예측합니다.
""")

oil = st.selectbox(
    "윤활유 종류",
    ["0W-20", "5W-30", "5W-40"]
)

distance = st.number_input(
    "현재 주행거리(km)",
    min_value=0,
    step=100
)

st.date_input("최근 교체일")

st.selectbox(
    "운행 환경",
    ["일반", "고속도로", "시내", "가혹조건"]
)

st.number_input(
    "평균 하루 주행거리(km)",
    min_value=1,
    value=30
)

if st.button("예측하기"):
    st.success("다음 단계에서 예측 모델을 연결합니다.")