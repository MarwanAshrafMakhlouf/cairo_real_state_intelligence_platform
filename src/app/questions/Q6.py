# q6_luxury_concentration.py
import streamlit as st
import plotly.express as px
import pandas as pd

def show_answer(df, selected_transaction):
    df = df.copy()

    if 'price_tier' not in df.columns:
        st.warning("Price tier data is not available.")
        return
    x_name = 'district'
    if df['district'].nunique() == 1:
        x_name = 'area'
        if df[x_name].nunique() == 1:
            x_name = 'neighborhood'
    tier_dist = (
        df.groupby([x_name, 'price_tier'])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    luxury_cols = [c for c in ['luxury', 'ultra_luxury'] if c in tier_dist.columns]

    if not luxury_cols:
        st.warning("Luxury tier data not found.")
        return

    tier_dist['total']       = tier_dist.drop(columns=x_name).sum(axis=1)
    tier_dist['luxury_pct']  = (tier_dist[luxury_cols].sum(axis=1) / tier_dist['total'] * 100).round(1)
    tier_dist = tier_dist[tier_dist['total'] >= 30]
    tier_dist = tier_dist.sort_values('luxury_pct', ascending=False)

    if tier_dist.empty:
        st.warning("Not enough data for the current filters.")
        return
    tier_dist = tier_dist[tier_dist['luxury_pct'] > 0]
    fig = px.bar(
        tier_dist,
        x=x_name,
        y='luxury_pct',
        text=tier_dist['luxury_pct'].apply(lambda x: f"{x:.1f}%"),
        color='luxury_pct',
        color_continuous_scale='Blues',
        labels={'luxury_pct': 'Luxury listings (%)', x_name: x_name.capitalize()},
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_tickangle=-45,
        margin=dict(l=0, r=20, t=20, b=80),
        height=450,
        yaxis_title='Luxury listings (%)',
        xaxis_title=None,
    )
    st.plotly_chart(fig, use_container_width=True)

    top    = tier_dist.iloc[0]
    second = tier_dist.iloc[1]
    avg    = tier_dist['luxury_pct'].mean()

    st.markdown(f"""
   ### Key Insights:
    - **{top[x_name]}** has the highest luxury concentration at **{top['luxury_pct']}%** of listings
    - **{second[x_name]}** follows at **{second['luxury_pct']}%**
    - Cairo average luxury concentration: **{avg:.1f}%**
    - Luxury is defined as listings in the top 5% of prices within their segment
    """)