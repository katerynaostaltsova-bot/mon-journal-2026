import streamlit as st

st.set_page_config(
    page_title="MON JOURNAL 2026",
    page_icon="❤️"
)

st.markdown("""
<style>
.stApp {
    background-color: #241019;
    color: #FFF0E9;
}
h1 {
    color: #D8A7B7 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("MON JOURNAL 2026")

st.write("Мой эстетичный бордовый планер")

st.checkbox("Выполнить планы на сегодня")
