import streamlit as st
import pandas as pd
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
st.title("FHM 검색")

question = st.text_input("증상 검색")

if st.button("검색"):

    df = pd.read_excel("experience_data.xlsx")

    data = df.to_string()

    prompt = f"""
다음은 복사기 AS 데이터다.

{data}

사용자 질문:
{question}

관련 사례를 찾아서
1. 주요 원인
2. 해결 방법

간단히 정리해라.
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    st.write(completion.choices[0].message.content)