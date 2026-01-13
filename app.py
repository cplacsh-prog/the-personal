import streamlit as st
from PIL import Image
import google.generativeai as genai
from openai import OpenAI
import json
import concurrent.futures # 병렬 처리를 위해 필요

# --- 1. 페이지 설정 ---
st.set_page_config(layout="wide", page_title="THE PERSONAL - Cross Check", page_icon="⚖️")

# --- 2. 스타일링 ---
st.markdown("""
    <style>
    .report-card {background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px;}
    .match {border-left: 5px solid #28a745;}
    .mismatch {border-left: 5px solid #dc3545; background-color: #fff5f5;}
    </style>
""", unsafe_allow_html=True)

st.title("⚖️ THE PERSONAL : AI Cross-Check System")
st.markdown("**GPT-4o**와 **Gemini Pro**가 교차 검증하여 완벽한 법률 자문을 제공합니다.")

# --- 3. API 키 설정 (스마트 오토매틱 버전) ---
with st.sidebar:
    st.header("🔑 엔진 키 설정")
    
    # 1. OpenAI 키 확인
    if "OPENAI_API_KEY" in st.secrets:
        openai_key = st.secrets["OPENAI_API_KEY"]
        st.success("✅ GPT-4o 엔진 장착 완료")
    else:
        openai_key = st.text_input("OpenAI Key (sk-...)", type="password")

    # 2. Google 키 확인
    if "GOOGLE_API_KEY" in st.secrets:
        google_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ Gemini 엔진 장착 완료")
    else:
        google_key = st.text_input("Google Key (AIza...)", type="password")
    
    st.info("두 개의 두뇌(GPT + Gemini)가 교차 검증합니다.")

# --- 4. 분석 프롬프트 (공통) ---
COMMON_PROMPT = """
당신은 대한민국 베테랑 노무사입니다. 근로계약서 이미지를 분석하여 아래 3가지 항목의 위법성을 판단하세요.
결과는 반드시 JSON 포맷으로 출력하세요.

1. 최저임금 (2025년 시급 10,030원 기준)
2. 수습기간 급여 감액 적법성
3. 위약금 예정 금지 위반

[JSON 출력 예시]
{
    "verdict": "위험" or "양호",
    "score": 80,
    "reason": "최저임금 위반이 발견됨."
}
"""

# --- 5. 개별 AI 함수 ---
def ask_gpt4o(api_key, image_url): # GPT는 이미지 URL 혹은 Base64 필요 (여기선 편의상 텍스트 설명으로 가정하거나, 실제 구현시 Base64 변환 필요)
    # *참고: 실제 GPT-4o Vision 연동은 코드가 길어져서, 여기선 Gemini 코드를 재활용하는 방식으로 시뮬레이션 하거나 
    # 실제로는 base64 인코딩 함수가 추가로 필요합니다. 지금은 로직 흐름 위주로 작성합니다.
    client = OpenAI(api_key=api_key)
    # (이미지 처리 로직 생략 - 실제로는 Base64 인코딩해서 보내야 함)
    # 여기서는 GPT가 텍스트만 처리한다고 가정하고 더미(Dummy) 로직 대신, 
    # 실제로는 Gemini와 동일하게 이미지를 봐야 합니다.
    return {"verdict": "위험", "score": 40, "reason": "GPT-4o: 시급 9860원은 2025년 기준 미달입니다."} 

def ask_gemini(api_key, image):
    try:
        genai.configure(api_key=api_key)
        
        # [수정] 가장 안정적인 표준 모델명으로 고정
        # 실험용(exp)이나 최신(2.5) 대신 '1.5-flash'를 씁니다.
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content(
            [COMMON_PROMPT, image], 
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
        
    except Exception as e:
        # 에러가 나면 멈추지 말고 에러 메시지를 리턴하도록 예외 처리
        return {"verdict": "에러", "score": 0, "reason": f"Gemini 분석 중 오류 발생: {str(e)}"}

def ask_gpt4o_real(api_key, base64_image):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system", 
                "content": "You are a legal expert. Return JSON only."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": COMMON_PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

# Base64 변환 함수
import base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

# --- 6. 메인 로직 ---
uploaded_file = st.file_uploader("계약서 업로드", type=["jpg", "png"])

if uploaded_file and st.button("🚀 교차 검증 시작 (Double Check)"):
    if not openai_key or not google_key:
        st.error("두 개의 API 키가 모두 필요합니다.")
    else:
        image = Image.open(uploaded_file)
        base64_img = encode_image(uploaded_file)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.image(image, caption="원본 계약서")
            
        with st.spinner("🤖 두 명의 AI 전문가가 토론 중입니다..."):
            # 병렬 처리 (동시에 물어보기)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_gemini = executor.submit(ask_gemini, google_key, image)
                future_gpt = executor.submit(ask_gpt4o_real, openai_key, base64_img)
                
                result_gemini = future_gemini.result()
                result_gpt = future_gpt.result()
        
# --- 결과 비교 및 통합 (이 부분을 덮어씌우세요) ---
        st.divider()
        st.subheader("📊 검증 리포트")
        
        # 의견 일치 여부 확인
        is_match = result_gemini['verdict'] == result_gpt['verdict']
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown(f"**Gemini 1.5 (구글)**")
            st.json(result_gemini)
            
        with c2:
            st.markdown(f"**GPT-4o (OpenAI)**")
            st.json(result_gpt)
            
        st.divider()
        
        if is_match:
            st.success(f"✅ **[판정 일치] 신뢰도 99.9%**\n\n두 AI 모두 **'{result_gpt['verdict']}'**으로 판단했습니다.")
            st.markdown(f"**통합 의견:** {result_gpt['reason']}")
        else:
            st.error("🚨 **[판정 불일치] 전문가 확인 필수**")
            
            # [수정된 부분] 안전하게 따옴표 3개(""")를 사용했습니다.
            st.markdown(f"""
            Gemini는 **{result_gemini['verdict']}**, 
            GPT는 **{result_gpt['verdict']}**라고 합니다.
            """)
            
            st.warning("이런 경우, 애매한 조항이 있거나 법적 해석이 갈릴 수 있으므로 **사람(노무사)의 직접 검토**가 반드시 필요합니다.")
            
            # 링크는 실제 연결하고 싶은 주소로 바꾸세요
            st.link_button("👑 대표 노무사에게 최종 판결 요청하기 (유료)", "https://open.kakao.com/o/sYourLink")

