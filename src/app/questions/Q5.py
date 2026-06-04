# q5_demand_velocity.py
import streamlit as st
import plotly.express as px
import pandas as pd

def show_answer(df, selected_transaction):
    df = df.copy()

    # derive is_removed from seller_name
    df['is_removed'] = df['seller_name'].str.strip().str.lower() == 'this ad is no longer available'
    x_name = 'district'
    if df['district'].nunique()== 1:
        x_name = 'area'
        if df['area'].nunique() == 1:
            x_name = 'neighborhood'
    velocity = (
        df.groupby(x_name)
            .agg(
                total=('is_removed', 'count'),
                removed=('is_removed', 'sum')
            )
            .reset_index()
        )
    velocity = velocity[velocity['total'] >= 20]
    velocity['turnover_rate'] = (velocity['removed'] / velocity['total'] * 100).round(1)
    velocity = velocity.sort_values('turnover_rate', ascending=False)

    if velocity.empty:
        st.warning("Not enough data for the current filters.")
        return

    fig = px.bar(
        velocity,
        x=x_name,
        y='turnover_rate',
        text=velocity['turnover_rate'].apply(lambda x: f"{x:.1f}%"),
        color='turnover_rate',
        color_continuous_scale='Blues',
        labels={'turnover_rate': 'Turnover rate (%)', x_name: x_name.capitalize()},
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_tickangle=-45,
        margin=dict(l=0, r=20, t=20, b=80),
        height=450,
        yaxis_title='Turnover rate (%)',
        xaxis_title=None,
    )
    st.plotly_chart(fig, use_container_width=True)

    top3    = velocity.head(3)
    bottom1 = velocity.iloc[-1]

    st.markdown(f"""
   ### Key Insights:
    - Highest demand: **{top3.iloc[0][x_name]}** at **{top3.iloc[0]['turnover_rate']}%** turnover
    - **{top3.iloc[1][x_name]}** and **{top3.iloc[2][x_name]}** follow at **{top3.iloc[1]['turnover_rate']}%** and **{top3.iloc[2]['turnover_rate']}%**
    - **{bottom1[x_name]}** has the slowest market at **{bottom1['turnover_rate']}%** turnover
    - Turnover rate reflects listings removed within the scraping window — a proxy for buyer demand velocity
    """)