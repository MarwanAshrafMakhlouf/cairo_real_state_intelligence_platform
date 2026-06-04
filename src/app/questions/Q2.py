# q2_size_vs_price.py
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

    # bin area into ranges
    bins   = [15, 75, 100, 125, 150, 175, 200, 250, 300, 400, 500, 800]
    labels = ['15-75', '76-100', '101-125', '126-150', '151-175',
            '176-200', '201-250', '251-300', '301-400', '401-500', '501-800']

    df['area_bin'] = pd.cut(df['area (m²)'], bins=bins, labels=labels)

    size_value = (
        df.groupby('area_bin', observed=True)['price_per_sqm']
        .agg(['median', 'count'])
        .reset_index()
    )
    size_value.columns = ['area_range_sqm', 'median_price_per_sqm', 'count']

    # drop bins with fewer than 30 listings
    size_value = size_value[size_value['count'] >= 20]

    if size_value.empty:
        st.warning("Not enough data across size ranges for the current filters.")
        return

    unit = "EGP/m²/month" if selected_transaction == "Rent" else "EGP/m²"

    fig = px.line(
        size_value,
        x='area_range_sqm',
        y='median_price_per_sqm',
        markers=True,
        labels={
            'area_range_sqm': 'Property size (m²)',
            'median_price_per_sqm': unit
        },
        text=size_value['median_price_per_sqm'].apply(lambda x: f"{x:,.0f}"),
    )
    fig.update_traces(
        textposition='top center',
        line_color='#378ADD',
        marker=dict(size=8, color='#185FA5')
    )
    fig.update_layout(
        margin=dict(l=0, r=20, t=20, b=20),
        height=420,
        yaxis_title=unit,
        xaxis_title='Property size (m²)',
    )
    st.plotly_chart(fig, use_container_width=True)

    # dynamic conclusion
    first_val = size_value.iloc[0]['median_price_per_sqm']
    last_val  = size_value.iloc[-1]['median_price_per_sqm']
    peak      = size_value.loc[size_value['median_price_per_sqm'].idxmax()]
    trough    = size_value.loc[size_value['median_price_per_sqm'].idxmin()]

    # determine actual shape
    if peak['area_range_sqm'] == size_value.iloc[0]['area_range_sqm']:
        shape_insight = f"Smaller properties command the highest price per m² — compact units are priced at a premium in this segment."
    elif peak['area_range_sqm'] == size_value.iloc[-1]['area_range_sqm']:
        shape_insight = f"Larger properties command the highest price per m² — size signals luxury in this segment."
    else:
        shape_insight = f"Price per m² peaks at **{peak['area_range_sqm']} m²** then declines — mid-size properties carry the premium in this segment."

    st.markdown(f"""
   ### Key Insights:
    - Best value per m² is found at **{trough['area_range_sqm']} m²** — **{trough['median_price_per_sqm']:,.0f} {unit}**
    - Highest price per m² is at **{peak['area_range_sqm']} m²** — **{peak['median_price_per_sqm']:,.0f} {unit}**
    - {shape_insight}
    """)