import streamlit as st
import pandas as pd
import plotly.express as px
from src.app.data_loader import load_data, location_loader
from src.app.components.sidebar import apply_sidebar_filters
from src.app.questions import Q1, Q2, Q3, Q4,Q5,Q6,Q7,Q8,Q9,Q10
import plotly.graph_objects as go

QUESTIONS = [
    "Select a question...",
    "1. Which location offer the best value per m²?",
    "2. How does property size affect price per m²?",
    "3. How does furnishing status affect price?",
    "4. How does property subtype affect pricing?",
    "5. Which areas have the highest demand velocity?",
    "6. Which location have the highest concentration of luxury listings?",
    "7. How do amenities affect price?",
    "8. Which location show the biggest gap between median and mean price?",
    "9. How does bedroom count affect price per m²?",
    "10. Off-plan vs ready — where is the premium?",
]
with st.spinner("Loading market data..."):
    df = load_data()
    locations = location_loader()
col_filter, col_main = st.columns([1, 3])
with col_filter:
    filtered_df, selected_type, selected_transaction, outlier_median = apply_sidebar_filters(df, locations)
with col_main:
    st.title("Market Explorer")
    st.write("Pick a question to get a focused answer based on"
             "your current sidebar filters.")
    selected = st.selectbox("What do you want to know?", QUESTIONS)
    if selected == "Select a question...":
        st.info("Choose a question above to get started.")
        st.stop()
    if selected.startswith("1."):
        Q1.show_anwer(filtered_df, selected_transaction)
    elif selected.startswith("2."):
        Q2.show_answer(filtered_df, selected_transaction)
    elif selected.startswith("3."):
        Q3.show_answer(filtered_df, selected_transaction)
    elif selected.startswith("4."):
        Q4.show_answer(filtered_df,selected_transaction)
    elif selected.startswith("5."):
        Q5.show_answer(filtered_df, selected_transaction)
    elif selected.startswith("6."):
        Q6.show_answer(filtered_df, selected_transaction)
    elif selected.startswith("7."):
        Q7.show_answer(filtered_df, selected_transaction)
    elif selected.startswith("8."):
        Q8.show_answer(filtered_df, selected_transaction)
    elif selected.startswith("9."):
        Q9.show_answer(filtered_df, selected_transaction)
    elif selected.startswith("10."):
        Q10.show_answer(filtered_df, selected_transaction)