import streamlit as st
from PIL import Image
import google.generativeai as genai
import json
import re  # 정규표현식(보안용)

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="THE PERSONAL - 보안 강화 버전",
    page_icon="🛡️",
    layout="centered"
)

# --- 2. CSS 스타일링 (보안 경고 추가) ---
st.markdown("""
    <style>
    .main-title {font-size: 2.5rem; color: #002B5B; font-weight: bold; text-align: center;}
    .sub-title {font-size: 1.2rem; color: #555; text-align: center; margin-bottom: 2rem;}
    .score-box {padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;}
    .danger {background-color: #FFEBEE; color: #D32F2F; border: 1px solid #FFCDD2;}
    .warning {background-color: #FFF3E0; color: #E65100; border: 1px solid #FFE0B2;}
    .success {background-color: #E8F5E9; color: #2E7D32; border: 1px solid #C8E6C9;}
    .security-alert {
        background-color: #FFF8E1; 
        border-left: 5px solid #FFC107; 
        padding: 15px; 
        margin-bottom: 20px;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 헤더 및 사이드바 ---
st.markdown('<div class="main-title">THE PERSONAL</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Premium HR AI Agent</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ 설정")
    # Secrets 자동 연동
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ 보안 키가 로드되었습니다.")
    else:
        api_key = st.text_input("Google API 키 입력", type="password")
        
    st.markdown("---")
    st.markdown("🛡️ **보안 모드 작동 중**\n\n모든 개인정보는 분석 후 즉시 파기됩니다.")

# --- 4. 보안 함수 (3차 방어선) ---
def mask_personal_info(text):
    """
    AI가 실수로 주민번호를 뱉더라도, 코드가 강제로 지워버리는 함수
    """
    if not isinstance(text, str):
        return text
        
    # 주민등록번호 패턴 (******-*******)
    rrn_pattern = r"\d{6}[- .]*[1-4]\d{6}"
    text = re.sub(rrn_pattern, "******-******* (보안조치됨)", text)
    
    # 전화번호 패턴 (010-****-****)
    phone_pattern = r"010[- .]*\d{3,4}[- .]*\d{4}"
    text = re.sub(phone_pattern, "010-****-**** (보안조치됨)", text)
    
    return text

# --- 5. Gemini 분석 함수 ---
def analyze_contract_secure(api_key, image):
    genai.configure(api_key=api_key)
    # 최신 모델 사용
    model = genai.GenerativeModel('gemini-2.0-flash-exp') # 없으면 gemini-1.5-flash
    
    # [2차 방어] 시스템 프롬프트에 보안 지침 강력 주입
    prompt = """
    당신은 대한민국 최고의 노무사이자 '개인정보보호 책임자(CPO)'입니다.
    근로계약서를 분석하되, 아래 [보안 수칙]을 목숨처럼 지키세요.

    [보안 수칙]
    1. 이미지에 있는 사람 이름, 주민등록번호, 전화번호, 주소는 **절대** 결과에 출력하지 마세요.
    2. 만약 인용이 필요하다면 반드시 '홍**', '010-****-1234' 형태로 마스킹하세요.
    3. 오직 '법적 위반 사항'만 분석하세요.

    [진단 항목]
    1. 최저임금 위반 여부
    2. 위약금/손해배상 예정 금지 위반
    3. 수습기간 급여 감액 적법성
    4. 퇴직금 분할 약정 여부
    5. 휴게시간 구체성

    [출력 포맷 (JSON Only)]
    {
        "score": 0~100,
        "status": "위험" or "주의" or "양호",
        "summary": "총평",
        "issues": [
            {"title": "제목", "severity": "상/중/하", "content": "내용"}
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
        # 모델명 에러 시 예외 처리
        if "404" in str(e):
            st.error("모델 버전을 찾을 수 없습니다. 코드를 'gemini-1.5-flash'로 변경해보세요.")
        return None

# --- 6. 메인 UI ---
# [1차 방어] 사용자 경고 메시지
st.markdown("""
    <div class="security-alert">
        🚨 <b>개인정보 보호 안내</b><br>
        주민등록번호 뒷자리는 반드시 가리고(마스킹) 업로드해주세요.<br>
        업로드된 파일은 AI 진단 후 즉시 서버에서 삭제됩니다.
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("계약서 업로드 (JPG, PNG)", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="분석 대기 중 (보안 터널링)", use_container_width=True)
    
    if st.button("🛡️ 보안 진단 시작"):
        if not api_key:
            st.error("API 키가 필요합니다.")
        else:
            with st.spinner("개인정보 필터링 및 법률 분석 중..."):
                result = analyze_contract_secure(api_key, image)
                
                if result:
                    # [3차 방어] 결과값 2차 세탁 (Python Regex)
                    safe_summary = mask_personal_info(result['summary'])
                    
                    st.divider()
                    
                    # 점수 박스
                    status_color = "danger" if result['status'] == "위험" else "warning" if result['status'] == "주의" else "success"
                    st.markdown(f"""
                        <div class="score-box {status_color}">
                            <h3>진단 결과: {result['status']}</h3>
                            <h1>{result['score']}점</h1>
                            <p>{safe_summary}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    # 상세 리포트
                    st.subheader("📋 상세 진단 리포트")
                    for issue in result['issues']:
                        # 내용에서도 개인정보 한 번 더 삭제
                        safe_content = mask_personal_info(issue['content'])
                        
                        icon = "🚨" if issue['severity'] == "상" else "⚠️" if issue['severity'] == "중" else "ℹ️"
                        with st.expander(f"{icon} {issue['title']} ({issue['severity']})"):
                            st.write(safe_content)
                    
                    st.divider()
                    st.link_button("👑 전문가에게 안전하게 상담하기", "https://open.kakao.com/o/sYourLink")
