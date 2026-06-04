# q8_mean_median_gap.py
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

def show_answer(df, selected_transaction):
    df = df.copy()
    df = df[df['price'].notna() & np.isfinite(df['price'])]

    if df.empty:
        st.warning("Not enough data for the current filters.")
        return
    x_name = 'district'
    if df['district'].nunique() == 1:
        x_name = 'area'
        if df['area'].nunique() == 1:
            x_name = 'neighborhood'
    gap_stats = (df.groupby(x_name)['price']
            .agg(['mean', 'median', 'count'])
            .reset_index()
            )
    gap_stats.columns = [x_name, 'mean_price', 'median_price', 'count']
    gap_stats = gap_stats[gap_stats['count'] >= 30]
    gap_stats['mean_median_ratio'] = (gap_stats['mean_price'] / gap_stats['median_price']).round(2)
    gap_stats = gap_stats.sort_values('mean_median_ratio', ascending=False)

    if gap_stats.empty:
        st.warning("Not enough listings per district for the current filters.")
        return

    fig = px.bar(
        gap_stats,
        x=x_name,
        y='mean_median_ratio',
        text=gap_stats['mean_median_ratio'].apply(lambda x: f"{x:.2f}x"),
        color='mean_median_ratio',
        color_continuous_scale='blues',
        labels={'mean_median_ratio': 'Mean / Median ratio', x_name: x_name.capitalize()},
    )
    fig.add_hline(
        y=1.0,
        line_dash='dash',
        line_color='gray',
        annotation_text='Perfectly symmetric (1.0x)',
        annotation_position='top right'
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_tickangle=-45,
        margin=dict(l=0, r=20, t=20, b=80),
        height=450,
        yaxis_title='Mean / Median ratio',
        xaxis_title=None,
    )
    st.plotly_chart(fig, use_container_width=True)

    most_skewed  = gap_stats.iloc[0]
    least_skewed = gap_stats.iloc[-1]

    st.markdown(f"""
   ### Key Insights:
    - **{most_skewed[x_name]}** has the highest mean-to-median ratio at **{most_skewed['mean_median_ratio']}x** — a small number of ultra-expensive listings are pulling the average well above the typical price
    - **{least_skewed[x_name]}** is the most uniform market at **{least_skewed['mean_median_ratio']}x** — prices are tightly clustered around the median
    - A ratio above **1.5x** signals that the advertised average price is misleading — the median is a better representation of what you will actually pay
    - Use the median, not the mean, when comparing districts with high ratios
    """)