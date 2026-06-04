# q3_furnishing.py
import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd

def show_answer(df, selected_transaction):
    df = df.copy()

    # drop unknown furnishing values
    df = df[df['furnished'].notna()]
    df = df[df['furnished'].str.lower().isin(['yes', 'no'])]

    if df.empty:
        st.warning("Not enough data for the current filters.")
        return

    # compute price per sqm
    df['price_per_sqm'] = df['price'] / df['area (m²)']
    df = df[df['price_per_sqm'].notna() & np.isfinite(df['price_per_sqm'])]

    # aggregate
    furnished_stats = (
        df.groupby('furnished')['price_per_sqm']
        .agg(['median', 'count'])
        .reset_index()
    )
    furnished_stats.columns = ['furnished', 'median_price_per_sqm', 'count']
    furnished_stats['furnished_label'] = furnished_stats['furnished'].map(
        {'yes': 'Furnished', 'no': 'Unfurnished'}
    )

    if len(furnished_stats) < 2:
        st.warning("Not enough data for both furnished and unfurnished in this segment.")
        return

    unit = "EGP/m²/month" if selected_transaction == "Rent" else "EGP/m²"

    fig = px.bar(
        furnished_stats,
        x='median_price_per_sqm',
        y='furnished_label',
        orientation='h',
        text=furnished_stats['median_price_per_sqm'].apply(lambda x: f"{x:,.0f}"),
        color='furnished_label',
        color_discrete_map={
            'Furnished': '#185FA5',
            'Unfurnished': '#85B7EB'
        },
        labels={
            'furnished_label': '',
            'median_price_per_sqm': unit
        },
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=20, t=20, b=20),
        height=300,
        xaxis_title=unit,
        yaxis_title=None,   
    )
    st.plotly_chart(fig, use_container_width=True)

    # dynamic conclusion
    furnished_val   = furnished_stats.loc[furnished_stats['furnished'] == 'yes', 'median_price_per_sqm'].values[0]
    unfurnished_val = furnished_stats.loc[furnished_stats['furnished'] == 'no',  'median_price_per_sqm'].values[0]
    premium         = (furnished_val - unfurnished_val) / unfurnished_val * 100

    furnished_count   = furnished_stats.loc[furnished_stats['furnished'] == 'yes', 'count'].values[0]
    unfurnished_count = furnished_stats.loc[furnished_stats['furnished'] == 'no',  'count'].values[0]

    if premium > 0:
        direction = f"Furnished properties command a **{premium:.1f}% premium** over unfurnished"
    else:
        direction = f"Unfurnished properties surprisingly command a **{abs(premium):.1f}% premium** over furnished in this segment"

    st.markdown(f"""
   ### Key Insights:
    - Furnished median: **{furnished_val:,.0f} {unit}** ({furnished_count:,} listings)
    - Unfurnished median: **{unfurnished_val:,.0f} {unit}** ({unfurnished_count:,} listings)
    - {direction}
    - {"This premium is strongest in rental markets where furnished units attract corporate tenants and expats" if selected_transaction == "Rent" else "In sale markets, furnished properties include fit-out costs which inflates the per m² figure"}
    """)