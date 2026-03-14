import os
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from openai import OpenAI

st.set_page_config(page_title="FHM", page_icon="🛠")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("FHM 검색")

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

gc = gspread.authorize(creds)

spreadsheet = gc.open("제목 없는 스프레드시트")
worksheet = spreadsheet.sheet1

records = worksheet.get_all_records()
df = pd.DataFrame(records)

question = st.text_input("증상 검색")

if st.button("검색"):

    data = df.to_string(index=False)

    prompt = f"""
다음은 복사기 및 업무 사례 데이터이다.

{data}

사용자 질문:
{question}

관련 사례를 찾아서 아래 형식으로 답해라.

1. 가능한 원인
2. 점검 순서
3. 조치 방법
4. 비슷한 사례 요약
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "너는 복사기 AS를 도와주는 회사 내부 AI다."},
            {"role": "user", "content": prompt}
        ],
    )

    answer = response.choices[0].message.content
    st.write(answer)
