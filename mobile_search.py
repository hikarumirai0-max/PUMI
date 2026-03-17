import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from openai import OpenAI

st.set_page_config(page_title="PUMI", page_icon="🐰", layout="wide")

SHEET_KEY = "1QRlW8IXoPjCyS1A4sIx0E4C1Z64Pa0hMmOWbfAOpn9g"

HEADERS = [
    "순번", "접수일", "월", "접수", "처리여부", "유입경로", "접수자", "처리자",
    "순2", "등급", "미수", "임대여부", "남은개월", "지역", "상호", "연락처",
    "자산번호", "기종", "시리얼번호", "증상", "처리내용", "비고", "특이사항",
    "일반전화", "확장성", "품목", "제조사", "기본금액", "연평균", "계약일",
    "종료일", "교체일", "주소", "기기상태", "시/도", "시/구", "방문주기",
    "납품담당", "키맨", "추가조건", "장비소유주", "위탁유지보수"
]

def load_data():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
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

ai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("PUMI 검색")

question = st.text_input("검색어", placeholder="예: N501 소음")

if st.button("검색") and question:
    try:
        with st.spinner("검색중..."):
            df = load_data()
st.write("데이터 로드 성공")

use_cols = ["상호", "기종", "증상", "처리내용", "비고", "특이사항"]
exist_cols = [c for c in use_cols if c in df.columns]

small_df = df[exist_cols].fillna("").astype(str).head(200)
text_data = small_df.to_string(index=False)

            prompt = f"""
{text_data}

질문: {question}
"""

            st.write("AI 요청 시작")

            response = ai_client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )

            st.write("AI 응답 받음")

            answer = response.output_text
            st.write(answer)

    except Exception as e:
        st.error(f"🔥 에러: {e}")
