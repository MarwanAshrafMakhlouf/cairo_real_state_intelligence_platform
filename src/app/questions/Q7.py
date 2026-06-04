# q7_amenities.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def show_answer(df, selected_transaction):
    df = df.copy()
    df['price_per_sqm'] = df['price'] / df['area (m²)']
    df = df[df['price_per_sqm'].notna() & np.isfinite(df['price_per_sqm'])]

    if df.empty:
        st.warning("Not enough data for the current filters.")
        return

    amenities = {
        'private_garden': 'Private garden',
        'balcony':        'Balcony',
        'pets_allowed':   'Pets allowed',
        'security':       'Security',
    }
    amenities = {k: v for k, v in amenities.items() if k in df.columns}

    if not amenities:
        st.warning("No amenity columns found in the dataset.")
        return

    results = []
    for col, label in amenities.items():
        with_val    = df[df[col] == 1]['price_per_sqm'].median()
        without_val = df[df[col] == 0]['price_per_sqm'].median()
        count_with  = (df[col] == 1).sum()
        count_without = (df[col] == 0).sum()

        if pd.notna(with_val) and pd.notna(without_val) and count_with >= 30 and count_without >= 30:
            premium = (with_val - without_val) / without_val * 100
            results.append({
                'amenity':       label,
                'with':          round(with_val, 0),
                'without':       round(without_val, 0),
                'premium_pct':   round(premium, 1),
                'count_with':    count_with,
                'count_without': count_without,
            })

    if not results:
        st.warning("Not enough data to compare amenities for the current filters.")
        return

    results_df = pd.DataFrame(results).sort_values('premium_pct', ascending=False)
    unit = "EGP/m²/month" if selected_transaction == "Rent" else "EGP/m²"

    # grouped bar chart — with vs without for each amenity
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='With amenity',
        x=results_df['amenity'],
        y=results_df['with'],
        text=results_df['with'].apply(lambda x: f"{x:,.0f}"),
        textposition='outside',
        marker_color='#185FA5',
    ))

    fig.add_trace(go.Bar(
        name='Without amenity',
        x=results_df['amenity'],
        y=results_df['without'],
        text=results_df['without'].apply(lambda x: f"{x:,.0f}"),
        textposition='outside',
        marker_color='#85B7EB',
    ))

    fig.update_layout(
        barmode='group',
        height=420,
        yaxis_title=unit,
        xaxis_title=None,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=0, r=20, t=40, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    # individual insight per amenity
    st.markdown("**Breakdown by amenity:**")
    for _, row in results_df.iterrows():
        direction = "adds" if row['premium_pct'] > 0 else "reduces"
        st.markdown(
            f"- **{row['amenity']}** {direction} **{abs(row['premium_pct']):.1f}%** to price per m² "
            f"— with: **{row['with']:,.0f}** vs without: **{row['without']:,.0f}** {unit} "
            f"({row['count_with']:,} vs {row['count_without']:,} listings)"
        )

    strongest = results_df.iloc[0]
    st.markdown(f"""
    ### Key Insights:
    - **{strongest['amenity']}** has the strongest price impact at **{strongest['premium_pct']:+.1f}%**
    - Premiums are computed by comparing median price per m² of properties with vs without each amenity in the current filtered segment
    """)