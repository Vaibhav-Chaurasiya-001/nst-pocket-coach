import streamlit as st
from ai import generate

st.set_page_config(page_title="Pocket Coach", page_icon="🤖")
st.title("Pocket Coach 🤖")

prompt = st.text_input("Say hi to Gemma:")
if st.button("Send"):
    with st.spinner("Thinking..."):
        reply = generate(prompt)
    st.write(reply)
