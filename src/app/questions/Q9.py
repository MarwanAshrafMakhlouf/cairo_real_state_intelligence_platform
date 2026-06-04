# q9_bedrooms.py
import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd

def show_answer(df, selected_transaction):
    df = df.copy()
    df['price_per_sqm'] = df['price'] / df['area (m²)']
    df = df[df['price_per_sqm'].notna() & np.isfinite(df['price_per_sqm'])]
    df = df[df['bedrooms'].notna()]

    df['bedroom_label'] = df['bedrooms'].apply(
        lambda x: '6+' if x >= 6 else str(int(x))
    )

    bedroom_order = ['1', '2', '3', '4', '5', '6+']

    bedroom_stats = (
        df.groupby('bedroom_label')['price_per_sqm']
        .agg(['median', 'count'])
        .reset_index()
    )
    bedroom_stats.columns = ['bedrooms', 'median_price_per_sqm', 'count']

    # apply minimum count but always keep 6+ if it exists
    bedroom_stats = bedroom_stats[
        (bedroom_stats['count'] >= 30) |
        (bedroom_stats['bedrooms'] == '6+')
    ]

    # force correct order without using Categorical which silently drops rows
    bedroom_stats['sort_order'] = bedroom_stats['bedrooms'].map(
        {label: i for i, label in enumerate(bedroom_order)}
    )
    bedroom_stats = bedroom_stats.dropna(subset=['sort_order'])
    bedroom_stats = bedroom_stats.sort_values('sort_order').drop(columns='sort_order')
    bedroom_stats = bedroom_stats.reset_index(drop=True)

    if bedroom_stats.empty:
        st.warning("Not enough data for the current filters.")
        return

    unit = "EGP/m²/month" if selected_transaction == "Rent" else "EGP/m²"

    fig = px.bar(
        bedroom_stats,
        x='bedrooms',
        y='median_price_per_sqm',
        text=bedroom_stats['median_price_per_sqm'].apply(lambda x: f"{x:,.0f}"),
        color='median_price_per_sqm',
        color_continuous_scale='Blues',
        labels={'bedrooms': 'Bedrooms', 'median_price_per_sqm': unit}
    )
    fig.update_xaxes(type='category')

    fig.update_traces(textposition='outside')
    fig.update_layout(
        coloraxis_showscale=False,
        margin=dict(l=0, r=20, t=20, b=20),
        height=420,
        yaxis_title=unit,
        xaxis_title='Number of bedrooms',
    )
    st.plotly_chart(fig, use_container_width=True)

    peak    = bedroom_stats.loc[bedroom_stats['median_price_per_sqm'].idxmax()]
    trough  = bedroom_stats.loc[bedroom_stats['median_price_per_sqm'].idxmin()]
    premium = (peak['median_price_per_sqm'] - trough['median_price_per_sqm']) / trough['median_price_per_sqm'] * 100

    st.markdown(f"""
### Key Insights:
- **{peak['bedrooms']}-bedroom** properties command the highest price per m² at **{peak['median_price_per_sqm']:,.0f} {unit}**
- **{trough['bedrooms']}-bedroom** properties offer the lowest price per m² at **{trough['median_price_per_sqm']:,.0f} {unit}**
- The difference between the highest and lowest is **{premium:.0f}%**
- More bedrooms do not always mean higher price per m² — larger units spread the cost across more space
    """)
