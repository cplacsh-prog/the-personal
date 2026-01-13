import streamlit as st
from PIL import Image
import google.generativeai as genai
import json
import re

# --- 1. 페이지 설정 (Wide Mode 적용) ---
st.set_page_config(
    page_title="THE PERSONAL - Pro Admin",
    page_icon="⚖️",
    layout="wide", # 화면을 넓게 씁니다 (전문가용 대시보드 느낌)
    initial_sidebar_state="expanded"
)

# --- 2. 고급 CSS 스타일링 (UX 개선) ---
st.markdown("""
    <style>
    /* 전체 폰트 및 배경 */
    .stApp {background-color: #f8f9fa;}
    
    /* 타이틀 스타일 */
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        color: #002B5B;
        font-weight: 700;
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #6c757d;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    /* 결과 카드 디자인 (Shadow 효과) */
    .result-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        border-left: 5px solid #ddd;
    }
    
    /* 상태별 색상 */
    .border-danger {border-left-color: #dc3545 !important;}
    .border-warning {border-left-color: #ffc107 !important;}
    .border-success {border-left-color: #28a745 !important;}
    
    /* 뱃지 스타일 */
    .badge {
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
    }
    .bg-danger {background-color: #dc3545;}
    .bg-warning {background-color: #ffc107; color: black;}
    .bg-success {background-color: #28a745;}
    </style>
""", unsafe_allow_html=True)

# --- 3. 사이드바 (설정 및 디버깅) ---
with st.sidebar:
    st.title("⚙️ PRO Settings")
    
    # API 키 관리
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ API Key Linked")
    else:
        api_key = st.text_input("Google API Key", type="password")
    
    st.divider()
    
    # 모델 선택 (성능 테스트용)
    model_option = st.selectbox(
        "AI 모델 선택",
        ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-pro-vision"],
        index=0
    )
    
    st.info("💡 'gemini-2.0-flash-exp'가 가장 똑똑합니다.")

# --- 4. 핵심 AI 로직 (프롬프트 고도화) ---
def analyze_contract_pro(api_key, image, model_name):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    # [성능 강화] 베테랑 노무사의 '판단 기준'을 주입 (Few-Shot Prompting)
    prompt = """
    당신은 대한민국 고용노동부 출신 30년 차 특별사법경찰관이자 노무사입니다.
    근로계약서를 픽셀 단위로 분석하여 '사용자(사장)'가 숨기려 하는 위법 사항을 적발하세요.
    
    [엄격한 판단 기준 (2025년 법령 적용)]
    1. **최저임금:** 2025년 시급 10,030원 미만이면 무조건 [위험]. 월급제인 경우 209시간 기준 2,096,270원 미만이면 [위험].
    2. **수습기간:** '단순노무직(편의점, 주유소, 식당 설거지 등)'은 수습 감액(90%)이 불법임. 직무가 모호하면 [주의] 경고.
    3. **휴게시간:** "휴게시간 있음"이라고만 쓰거나, "손님 없을 때 쉰다"는 문구는 [위험]. 구체적 시간(예: 12:00~13:00)이 없으면 지적할 것.
    4. **포괄임금:** 기본급과 제수당(연장,야간 등)이 구분되지 않고 '월급 300만원' 식으로 뭉뚱그려져 있으면 [위험].
    5. **위약금:** "퇴사 시 월급 반환", "손해배상 청구" 문구 발견 시 즉시 [위험].

    [출력 포맷 (JSON)]
    반드시 JSON만 출력하세요.
    {
        "total_score": 0~100,
        "final_verdict": "위험" or "주의" or "양호",
        "summary_comment": "날카롭고 직설적인 한 줄 총평",
        "details": [
            {
                "category": "최저임금",
                "status": "위험" or "주의" or "양호",
                "finding": "계약서상 시급 9,860원은 2025년 법정 최저임금(10,030원) 위반임."
            },
            ... (나머지 4개 항목)
        ]
    }
    """

    try:
        response = model.generate_content(
            [prompt, image],
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e)}

# --- 5. 메인 UI 구성 (2단 레이아웃) ---
st.markdown('<div class="main-header">THE PERSONAL <span style="font-size:1rem; vertical-align:middle; color:#888;">PRO DASHBOARD</span></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">베테랑 노무사의 눈으로 검토합니다.</div>', unsafe_allow_html=True)

# 레이아웃 분할 (좌측: 입력 / 우측: 결과)
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📄 계약서 확인")
    uploaded_file = st.file_uploader("계약서 이미지를 올려주세요", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="원본 이미지", use_container_width=True)

with col2:
    st.markdown("### 📊 분석 리포트")
    
    if uploaded_file and api_key:
        if st.button("🚀 정밀 진단 실행 (Start Audit)", type="primary", use_container_width=True):
            with st.spinner("🔍 2025년 최신 판례 대조 중..."):
                result = analyze_contract_pro(api_key, image, model_option)
                
                if "error" in result:
                    st.error(f"분석 중 오류 발생: {result['error']}")
                else:
                    # 1. 종합 점수 패널
                    verdict_color = "border-danger" if result['final_verdict'] == "위험" else "border-warning" if result['final_verdict'] == "주의" else "border-success"
                    badge_class = "bg-danger" if result['final_verdict'] == "위험" else "bg-warning" if result['final_verdict'] == "주의" else "bg-success"
                    
                    st.markdown(f"""
                        <div class="result-card {verdict_color}">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span class="badge {badge_class}">{result['final_verdict']}</span>
                                <h2 style="margin:0; color:#333;">{result['total_score']}점</h2>
                            </div>
                            <hr style="margin:10px 0;">
                            <p style="font-weight:bold; font-size:1.1rem;">"{result['summary_comment']}"</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # 2. 상세 항목별 카드
                    for item in result['details']:
                        status_icon = "❌" if item['status'] == "위험" else "⚠️" if item['status'] == "주의" else "✅"
                        item_color = "border-danger" if item['status'] == "위험" else "border-warning" if item['status'] == "주의" else "border-success"
                        
                        st.markdown(f"""
                            <div class="result-card {item_color}" style="padding:15px;">
                                <strong>{status_icon} {item['category']}</strong>
                                <p style="margin-top:5px; margin-bottom:0; font-size:0.95rem; color:#555;">{item['finding']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # 3. 피드백 루프 (개발자 모드)
                    with st.expander("🛠️ 개발자용 원본 데이터 확인 (JSON)"):
                        st.json(result)

    elif not uploaded_file:
        st.info("👈 왼쪽에서 파일을 먼저 업로드해주세요.")
    elif not api_key:
        st.warning("⚠️ 사이드바에서 API 키를 설정해주세요.")
