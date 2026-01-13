import streamlit as st
from PIL import Image
import google.generativeai as genai
import json
import re

# ... (기존 설정 및 CSS 코드는 그대로 유지) ...
# (만약 전체 코드가 필요하면 말씀해주세요. 핵심 변경 부분만 드립니다.)

def analyze_contract_advanced(api_key, image):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp') # 또는 1.5-flash
    
    # [베테랑의 비기: Chain of Thought 프롬프트]
    # AI에게 생각할 순서를 강제하여 정확도를 획기적으로 높입니다.
    prompt = """
    당신은 대한민국 대법원 판례와 노동법에 통달한 'AI 노무 전문 위원'입니다.
    제공된 근로계약서 이미지를 [Step-by-Step]으로 정밀 분석하여 법적 리스크를 찾아내세요.

    [분석 절차]
    1. **OCR 판독**: 이미지 내의 모든 텍스트를 정확하게 읽으세요. (금액, 날짜, 숫자 주의)
    2. **조항 대조**: 읽어낸 텍스트를 최신 근로기준법(2025/2026 기준) 및 관련 판례와 대조하세요.
    3. **리스크 판단**: 단순 위반뿐만 아니라, '애매한 문구'로 인한 분쟁 가능성까지 찾아내세요.
    4. **결과 출력**: 반드시 지정된 JSON 형식으로만 답하세요.

    [핵심 점검 체크리스트 (Strict Mode)]
    1. **최저임금**: 2025년(10,030원), 2026년 예상치 등을 고려하여 시급 환산액이 미달되는지 계산하세요.
    2. **포괄임금제 오남용**: '기본급'과 '고정연장수당'이 명확히 구분되지 않고 뭉뚱그려져 있는지(유효성) 확인하세요.
    3. **위약금/손해배상**: 퇴사 시 '임금 반환', '배상' 등의 키워드가 포함된 독소 조항(근기법 제20조 위반)을 찾으세요.
    4. **휴게시간**: '휴게시간 있음'이라고만 쓰고 구체적 시간(예: 12:00~13:00)이 없는지(명시 의무 위반) 확인하세요.
    5. **수습기간**: 1년 미만 계약자에게 수습 감액(90%)을 적용했는지(불법) 확인하세요.

    [출력 포맷 (JSON)]
    {
        "score": (0~100점, 위반이 많을수록 감점),
        "status": "위험" | "주의" | "양호",
        "summary": "사장님/근로자에게 해주는 3줄 요약 조언 (친절하지만 단호하게)",
        "issues": [
            {
                "category": "최저임금" | "계약기간" | "휴게시간" | "독소조항" | "기타",
                "detected_text": "계약서에서 문제가 된 실제 문장 그대로 인용 (중요)",
                "legal_basis": "관련 법 조항 (예: 근로기준법 제xx조)",
                "reasoning": "왜 이것이 문제가 되는지 구체적 설명",
                "severity": "상" | "중" | "하"
            }
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
        st.error(f"분석 중 오류 발생: {str(e)}")
        return None

# ... (UI 부분은 기존과 동일하되, 함수 이름만 analyze_contract_advanced로 변경하여 호출) ...
