import streamlit as st
from PIL import Image
import google.generativeai as genai
import json

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="THE PERSONAL - AI 노무 진단 (Gemini Ver)",
    page_icon="⚖️",
    layout="centered"
)

# --- 2. CSS 스타일링 ---
st.markdown("""
    <style>
    .main-title {font-size: 2.5rem; color: #002B5B; font-weight: bold; text-align: center;}
    .sub-title {font-size: 1.2rem; color: #555; text-align: center; margin-bottom: 2rem;}
    .score-box {padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;}
    .danger {background-color: #FFEBEE; color: #D32F2F; border: 1px solid #FFCDD2;}
    .warning {background-color: #FFF3E0; color: #E65100; border: 1px solid #FFE0B2;}
    .success {background-color: #E8F5E9; color: #2E7D32; border: 1px solid #C8E6C9;}
    </style>
""", unsafe_allow_html=True)

# --- 3. 헤더 및 사이드바 ---
st.markdown('<div class="main-title">THE PERSONAL</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Powered by Google Gemini</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ 설정")
    # 구글 API 키 입력받기
    api_key = st.text_input("Google API 키를 입력하세요", type="password")
    st.info("※ [aistudio.google.com]에서 무료로 발급 가능합니다.")
    st.markdown("---")
    st.markdown("**노무사 사무소 퍼스널**\n\n문의: 02-0000-0000")

# --- 4. Gemini 분석 함수 ---
def analyze_contract_gemini(api_key, image):
    # 구글 API 설정
    genai.configure(api_key=api_key)
    
    # 모델 설정 (Gemini 1.5 Flash가 빠르고 저렴하며 Vision에 최적화됨)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = """
    당신은 20년 차 베테랑 노무사 'THE PERSONAL'입니다. 
    제공된 근로계약서 이미지를 분석하여 아래 5가지 핵심 리스크를 진단하세요.
    
    [진단 항목]
    1. 최저임금 위반 (2025/2026년 기준 시급 체크)
    2. 위약금/손해배상 예정 금지 위반 (근로기준법 제20조)
    3. 수습기간 급여 감액 적법성 (단순노무직 여부 등)
    4. 퇴직금 분할 약정 (월급에 포함 여부)
    5. 휴게시간 구체성 (시간대 명시 여부)

    [출력 포맷]
    반드시 아래 JSON 형식으로만 출력하세요. 마크다운 기호(```json)는 쓰지 마세요.
    {
        "score": 0~100 사이의 정수 점수,
        "status": "위험" 또는 "주의" 또는 "양호",
        "summary": "전체적인 총평 한 문장",
        "issues": [
            {"title": "위반 항목 제목", "severity": "상/중/하", "content": "구체적인 위반 내용과 법적 근거"}
        ]
    }
    """

    # Gemini에게 이미지와 프롬프트를 함께 전송
    # response_mime_type을 json으로 설정하여 정확도 향상
    response = model.generate_content(
        [prompt, image],
        generation_config={"response_mime_type": "application/json"}
    )
    
    return json.loads(response.text)

# --- 5. 메인 UI 로직 ---
uploaded_file = st.file_uploader("근로계약서 사진이나 파일을 업로드하세요 (JPG, PNG)", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # 이미지를 화면에 표시
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 계약서", use_container_width=True)
    
    if st.button("🔍 Gemini AI 정밀 진단 시작"):
        if not api_key:
            st.error("좌측 사이드바에 Google API 키를 먼저 입력해주세요.")
            st.markdown("[👉 Google API 키 발급받기 (무료)](https://aistudio.google.com/app/apikey)")
        else:
            with st.spinner("Gemini가 계약서를 꼼꼼히 읽고 있습니다..."):
                try:
                    result = analyze_contract_gemini(api_key, image)
                    
                    # --- 결과 출력 ---
                    st.divider()
                    
                    # 1. 점수 박스
                    status_color = "danger" if result['status'] == "위험" else "warning" if result['status'] == "주의" else "success"
                    st.markdown(f"""
                        <div class="score-box {status_color}">
                            <h3>진단 결과: {result['status']}</h3>
                            <h1>{result['score']}점</h1>
                            <p>{result['summary']}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    # 2. 상세 리포트
                    st.subheader("📋 상세 진단 리포트")
                    for issue in result['issues']:
                        icon = "🚨" if issue['severity'] == "상" else "⚠️" if issue['severity'] == "중" else "ℹ️"
                        with st.expander(f"{icon} {issue['title']} ({issue['severity']})"):
                            st.write(issue['content'])

                    # 3. 전문가 매칭
                    st.divider()
                    st.info("💡 AI 진단은 참고용입니다. 법적 보호가 필요하신가요?")
                    st.link_button("👑 노무사 사무소 퍼스널 연결 (30,000원)", "[https://open.kakao.com/o/sYourLink](https://open.kakao.com/o/sYourLink)")

                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")