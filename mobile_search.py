import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from openai import OpenAI

# =========================
# 0. 앱 설정
# =========================
st.set_page_config(page_title="PUMI", page_icon="🐰", layout="wide")

# =========================
# 1. 설정값 (여기만 수정)
# =========================
APP_TITLE = "PUMI"
APP_SUBTITLE = "Powered by 퍼스트전산"
APP_GUIDE = "AS / 계약 / IT 문의를 한 번에 검색할 수 있습니다."

# 구글 시트 키 (URL에서 /d/ 뒤 부분)
SHEET_KEY = "1QRlW8IXoPjCyS1A4sIx0E4C1Z64Pa0hMmOWbfAOpn9g"

# 헤더
HEADERS = [
    "순","접수일","월","접수","처리여부","유입경로","접수자","처리자",
    "순2","등급","미수","임대여부","남은개월","지역","상호","연락처",
    "자산번호","기종","시리얼번호","증상","처리내용","비고","특이사항",
    "일반전화","확장성","품목","제조사","기본금액","연평균","계약일",
    "종료일","교체일","주소","기기상태","시/도","시/구","방문주기",
    "납품담당","키맨","추가조건","장비소유주","위탁유지보수"
]

# =========================
# 2. 구글 시트 연결 (건드리지 말 것)
# =========================
def load_data():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly"
        ],
    )

    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SHEET_KEY)
    worksheets = sheet.worksheets()
    frames = []

    for ws in worksheets:
        data = ws.get_all_values()
        rows = data[2:]
        cleaned = [r[:len(HEADERS)] + [""] * (len(HEADERS) - len(r)) for r in rows]
        if cleaned:
            frames.append(pd.DataFrame(cleaned, columns=HEADERS))

    if not frames:
        return pd.DataFrame(columns=HEADERS)

    df = pd.concat(frames, ignore_index=True)
    df = df.fillna("").astype(str)
    return df

# =========================
# 3. OpenAI 연결
# =========================
ai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# =========================
# 4. UI
# =========================
st.markdown(
    f"""
    <div style="text-align:center;">
        <h1>{APP_TITLE}</h1>
        <div>{APP_SUBTITLE}</div>
        <div style="margin-top:8px;">{APP_GUIDE}</div>
    </div>
    """,
    unsafe_allow_html=True
)

question = st.text_input("", placeholder="예: 용지걸림 / 계약 언제 끝나?")

if st.button("검색") and question:
    with st.spinner("검색중..."):
        df = load_data()
        text_data = df.to_string(index=False)

        prompt = f"""
다음은 회사 데이터다.

{text_data}

질문:
{question}

아래 형식으로 답변:
1. 원인
2. 해결방법
3. 참고사항
"""

        response = ai_client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        answer = response.output_text

        st.markdown("## 결과")
        st.write(answer)
