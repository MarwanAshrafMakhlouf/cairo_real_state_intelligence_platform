import streamlit as st

st.set_page_config(page_title="Cairo Real Estate Intelligence Platform", 
                   page_icon="🏢"
                   ,layout="wide")
# main.py




pg = st.navigation([
    st.Page("src/app/pages/home.py", title="Home"),
    st.Page("src/app/pages/overview.py", title="Market Overview"),
    st.Page("src/app/pages/explorer.py", title="Market Explorer"),
    st.Page("src/app/pages/estimator.py", title="Price Estimator"),
    st.Page("src/app/pages/chatbot.py", title="Market Chatbot"),
])

pg.run()