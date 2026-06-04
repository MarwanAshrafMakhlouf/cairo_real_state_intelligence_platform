# q4_subtype_pricing.py
import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd

def show_answer(df, selected_transaction):
    df = df.copy()
    df['price_per_sqm'] = df['price'] / df['area (m²)']
    df = df[df['price_per_sqm'].notna() & np.isfinite(df['price_per_sqm'])]

    if df.empty:
        st.warning("Not enough data for the current filters.")
        return

    subtype_stats = (
        df.groupby('property_subtype')['price_per_sqm']
        .agg(['median', 'count'])
        .reset_index()
    )
    subtype_stats.columns = ['property_subtype', 'median_price_per_sqm', 'count']
    subtype_stats = subtype_stats[subtype_stats['count'] >= 30]
    subtype_stats = subtype_stats.sort_values('median_price_per_sqm', ascending=True)

    if subtype_stats.empty:
        st.warning("Not enough listings per subtype for the current filters.")
        return

    unit = "EGP/m²/month" if selected_transaction == "Rent" else "EGP/m²"

    fig = px.bar(
        subtype_stats,
        x='median_price_per_sqm',
        y='property_subtype',
        orientation='h',
        text=subtype_stats['median_price_per_sqm'].apply(lambda x: f"{x:,.0f}"),
        color='median_price_per_sqm',
        color_continuous_scale='Blues',
        labels={'median_price_per_sqm': unit, 'property_subtype': 'Property subtype'},
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        coloraxis_showscale=False,
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title=unit,
        yaxis_title=None,
        margin=dict(l=0, r=40, t=20, b=20),
        height=max(350, len(subtype_stats) * 50),
    )
    st.plotly_chart(fig, use_container_width=True)

    highest = subtype_stats.iloc[-1]
    lowest  = subtype_stats.iloc[0]
    premium = (highest['median_price_per_sqm'] - lowest['median_price_per_sqm']) / lowest['median_price_per_sqm'] * 100

    st.markdown(f"""
   ### Key Insights:
    - **{highest['property_subtype']}** commands the highest price at **{highest['median_price_per_sqm']:,.0f} {unit}**
    - **{lowest['property_subtype']}** is the most affordable at **{lowest['median_price_per_sqm']:,.0f} {unit}**
    - The premium between the most and least expensive subtype is **{premium:.0f}%**
    """)