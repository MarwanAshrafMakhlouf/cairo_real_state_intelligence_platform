# q10_offplan_vs_ready.py
import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd

def show_answer(df, selected_transaction):
    if selected_transaction == "Rent":
        st.warning("Off-plan vs ready comparison is only meaningful for sale listings. Switch the transaction filter to Sale for this analysis.")
        return

    df = df.copy()
    df['price_per_sqm'] = df['price'] / df['area (m²)']
    df = df[df['price_per_sqm'].notna() & np.isfinite(df['price_per_sqm'])]
    df = df[df['completion status'].isin(['ready', 'off-plan'])]

    if df.empty:
        st.warning("Not enough data for the current filters.")
        return

    # overall comparison
    overall = (
        df.groupby('completion status')['price_per_sqm']
        .agg(['median', 'count'])
        .reset_index()
    )
    overall.columns = ['completion status', 'median_price_per_sqm', 'count']
    x_name = 'district'
    if df['district'].nunique() == 1:
        x_name = 'area'
        if df['area'].nunique() == 1:
            x_name = 'neighborhood'

    # by district
    district_comp = (
        df.groupby([x_name, 'completion status'])['price_per_sqm']
        .median()
        .unstack()
        .reset_index()
    )
    district_comp.columns = [x_name, 'off-plan', 'ready']
    district_comp = district_comp.dropna()

    counts = df.groupby(x_name).size()
    reliable = counts[counts >= 30].index
    district_comp = district_comp[district_comp[x_name].isin(reliable)]

    district_comp['premium_pct'] = (
        (district_comp['off-plan'] - district_comp['ready']) /
        district_comp['ready'] * 100
    ).round(1)
    district_comp = district_comp.sort_values('premium_pct', ascending=True)

    if district_comp.empty:
        st.warning("Not enough data per district for the current filters.")
        return

    fig = px.bar(
        district_comp,
        x=x_name,
        y='premium_pct',
        text=district_comp['premium_pct'].apply(lambda x: f"{x:+.1f}%"),
        color='premium_pct',
        color_continuous_scale='Blues',
        color_continuous_midpoint=0,
        labels={'premium_pct': 'Off-plan vs ready (%)', x_name: x_name.capitalize()},
    )
    fig.add_hline(y=0, line_dash='dash', line_color='gray')
    fig.update_traces(textposition='outside')
    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_tickangle=-45,
        margin=dict(l=0, r=20, t=20, b=80),
        height=450,
        yaxis_title='Off-plan price premium vs ready (%)',
        xaxis_title=None,
    )
    st.plotly_chart(fig, use_container_width=True)

    # overall numbers
    ready_median   = overall.loc[overall['completion status'] == 'ready',    'median_price_per_sqm'].values[0]
    offplan_median = overall.loc[overall['completion status'] == 'off-plan', 'median_price_per_sqm'].values[0]
    overall_diff   = (offplan_median - ready_median) / ready_median * 100

    most_premium  = district_comp.iloc[-1]
    most_discount = district_comp.iloc[0]

    direction = "premium" if overall_diff > 0 else "discount"

    st.markdown(f"""
   ### Key Insights:
    - Overall, off-plan listings trade at a **{abs(overall_diff):.1f}% {direction}** vs ready units
    - **{most_premium[x_name]}** shows the largest off-plan premium at **{most_premium['premium_pct']:+.1f}%** — investors are paying for future delivery in this high-demand area
    - **{most_discount[x_name]}** shows the largest off-plan discount at **{most_discount['premium_pct']:+.1f}%** — buyers can find value in pre-delivery units here
    - Positive = off-plan costs more than ready. Negative = off-plan is cheaper than ready.
    """)