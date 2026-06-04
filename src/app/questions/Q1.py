import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px

def show_anwer(df, selected_transaction):
    # compute price per sqm
    df = df.copy()
    df['price_per_sqm'] = df['price'] / df['area (m²)']
    df = df[df['price_per_sqm'].notna() & np.isfinite(df['price_per_sqm'])]

    if df.empty:
        st.warning("Not enough data for the current filters.")
        return
    
    y_name = 'district'
    if df['district'].nunique() == 1:
        y_name = 'area'
        if df['area'].nunique() == 1:
            y_name = 'neighborhood'
    district_stats = (
            df.groupby(y_name)['price_per_sqm']
            .agg(['median', 'count'])
            .reset_index()
            )   
    district_stats.columns = [y_name, 'median_price_per_sqm', 'listing_count']
        

    # minimum 30 listings for reliability
    district_stats = district_stats[district_stats['listing_count'] >= 20]
    district_stats = district_stats.sort_values('median_price_per_sqm', ascending=True)

    if district_stats.empty:
        st.warning("Not enough listings per district for the current filters.")
        return

    # chart
    unit = "EGP/m²/month" if selected_transaction == "Rent" else "EGP/m²"

    fig = px.bar(
        district_stats,
        x='median_price_per_sqm',
        y=y_name,
        orientation='h',
        text=district_stats['median_price_per_sqm'].apply(lambda x: f"{x:,.0f}"),
        labels={'median_price_per_sqm': unit, y_name: y_name.capitalize()},
        color='median_price_per_sqm',
        color_continuous_scale='Blues',
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        coloraxis_showscale=False,
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title=unit,
        yaxis_title=None,
        margin=dict(l=0, r=40, t=20, b=20),
        height=max(400, len(district_stats) * 35),
    )
    st.plotly_chart(fig, use_container_width=True)

    # dynamic conclusion
    best      = district_stats.iloc[0]
    worst     = district_stats.iloc[-1]
    cairo_med = district_stats['median_price_per_sqm'].median()
    premium   = (worst['median_price_per_sqm'] - best['median_price_per_sqm']) / best['median_price_per_sqm'] * 100

    st.markdown(f"""
    ### Key Insights:
    - **{best[y_name]}** offers the best value at **{best['median_price_per_sqm']:,.0f} {unit}**
    - **{worst[y_name]}** commands the highest price at **{worst['median_price_per_sqm']:,.0f} {unit}**
    - The most expensive {y_name} costs **{premium:.0f}% more** per m² than the cheapest
    - Cairo median for this segment: **{cairo_med:,.0f} {unit}**
    """)