import streamlit as st
import pandas as pd
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("FHM AI")

# 대화 기록 저장
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 출력
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 사용자 입력
prompt = st.chat_input("증상이나 문제를 입력하세요")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 엑셀 데이터 불러오기
    df = pd.read_excel("experience_data.xlsx")
    knowledge = df.to_string()

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": f"다음은 복사기 AS 경험 데이터다:\n{knowledge}"},
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)
