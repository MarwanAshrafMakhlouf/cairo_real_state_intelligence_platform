import streamlit as st
import plotly.express as px
from src.app.data_loader import load_data, location_loader
from src.app.components.sidebar import apply_sidebar_filters
import plotly.graph_objects as go
with st.spinner("Loading market data..."):
    df = load_data()
    locations = location_loader()
col_filter, col_main = st.columns([1, 3])
with col_filter:
    filtered_df, selected_type, selected_transaction, outlier_median = apply_sidebar_filters(df, locations)
   
with col_main:
    st.subheader("Market Overview")
    if filtered_df.empty:
        st.warning("No listings match your current filters. Try adjusting your selection.")
        st.stop()
    col, col1, col2, col3 = st.columns(4)
    with col:
        st.markdown("**Total listings**")
        st.markdown(f"### {len(df):,.0f}")
        st.markdown("**Across all segments**")
    with col1:
        st.markdown(f"**Listings in {selected_type}**")
        st.markdown(f"### {len(filtered_df):,.0f}")
        st.markdown(f"**For {selected_transaction}**")
       
    with col2:
        if selected_transaction == 'Rent':
            st.markdown(f"**Median Price for {selected_type}**")
            st.markdown(f"### {filtered_df['price'].median()/1000:,.0f}K EGP")
            st.markdown(f"**For {selected_transaction}**")
        else:
            st.markdown(f"**Median Price for {selected_type}**")
            st.markdown(f"### {filtered_df['price'].median()/1000000:,.1f}M EGP")
            st.markdown(f"**For {selected_transaction}**")
    with col3:
        st.markdown(f"**Most Active District**")
        st.markdown(f"### {filtered_df['district'].mode()[0]}")
        st.markdown("**Highest Volume**")

    # Draw first divider
    st.divider()
    pie_chart , bar_chart = st.columns([1, 2])
  
    with pie_chart:
        # build segment labels from your actual columns
        df["segment"] = df["property_type"] + " " + df["sale_or_rent"].str.lower()

        segment_counts = df["segment"].value_counts().reset_index()
        segment_counts.columns = ["segment", "count"]

        fig = px.pie(
            segment_counts,
            values="count",
            names="segment",
            hole=0.5,  # this makes it a donut
            title="Listings by segment"
        )

        fig.update_traces(
            textinfo="percent",
            hovertemplate="%{label}<br>%{value:,} listings<br>%{percent}"
        )

        fig.update_layout(
            legend=dict(orientation="v"),
            title_subtitle_text=f"Share of total {len(df):,} listings"
        )

        st.plotly_chart(fig, use_container_width=True)
    with bar_chart:
    
        if filtered_df['district'].nunique() > 1:
            x_name = "district"
            
        elif filtered_df['area'].nunique() >1:
            x_name = "area"
        elif filtered_df['neighborhood'].nunique() >1:
            x_name = "neighborhood"
        else: 
            x_name = "district"
        
        stats = (
            filtered_df.groupby(x_name)["price"]
            .agg(["count", "mean", "median"])
            .sort_values("mean", ascending=False)
            .reset_index()
        )
        fig2 = go.Figure()
        fig2.add_trace( go.Bar(
            x=stats[x_name], y = stats['mean'],
            name = "Mean Price", yaxis="y1"
            )
        )
        fig2.add_trace(
            go.Bar(
                x=stats[x_name], y=stats['median'],
                name= "Median pric", yaxis="y1"
            )
        )
        fig2.add_trace(
            go.Scatter(
                x=stats[x_name], y=stats['count'],
                name = "Listing count", yaxis="y2",
                mode="lines+markers"
            )
        )

        fig2.update_layout(
            title = f"Mean, Median, and listing count by {x_name}",
            barmode="group",
            xaxis=dict(tickangle=-90),
            yaxis = dict(title="Price EGP"),
            yaxis2= dict(title ="Number of listings", overlaying ="y",side ="right"),
            legend = dict(orientation="h",y=1.1)
        )
        st.plotly_chart(fig2, use_container_width=True)
        # the last section 
    st.divider()
    price_tier, scatter_plot = st.columns([1,2])

    
    with price_tier:
            data = filtered_df['price_tier'].value_counts().reset_index()
            data.columns = ["tier", "count"]
            data["percentage"] = (data["count"]/data["count"].sum()*100).round(1)
            data = data.sort_values("percentage", ascending = False)

            fig4 = px.bar(
                data,
                x = "percentage",
                y = "tier",
                orientation="h",
                title ="Price tier distribution",
                text = data['percentage'].apply(lambda x:f"{x}%")
            )

            fig4.update_traces(
                textposition="outside"
            )
            fig4.update_layout(
                xaxis_title = "Listings (%)",
                yaxis_title="",
                xaxis=dict(range=[0,110])
            )
            st.plotly_chart(fig4, use_container_width=True)
    with scatter_plot:
            x_cap = filtered_df['area (m²)'].quantile(0.99)
            y_cap = filtered_df['price'].quantile(0.99)

            plot_data = filtered_df[(filtered_df['area (m²)'] < x_cap) & (filtered_df['price'] < y_cap)]
            fig3 = px.scatter(plot_data, 
                              x = 'area (m²)', 
                              y = 'price',
                              color='price_tier',
                              title = 'Price vs Area')
            st.plotly_chart(fig3, use_container_width=True)
    st.divider()
    st.markdown("> Note: Top 1% of the values are excluded for clearer visualization")
    if selected_transaction == 'Rent':
        st.markdown(f"> As the top 1% {selected_type.lower()}s  have a median {selected_transaction.lower()} price of {outlier_median/1000:,.0f}K EGP" )
    else:
        st.markdown(f"> As the top 1% {selected_type.lower()}s  have a median {selected_transaction.lower()} price of {outlier_median/1000000:,.0f}M EGP" )
    st.divider()
    st.markdown("### What does this tell us?")

    top_district = df["district"].value_counts().index[0]
    median_sale = filtered_df["price"].median()
    mean_sale = filtered_df["price"].mean()
    skew = filtered_df["price"].skew()

    skew_comment = "pushed upward by a small number of high-value listings" if skew > 1 else "relatively balanced with no extreme outliers"

    st.markdown(f"""
    - The gap between mean and median prices suggests the distribution is **{skew_comment}** — 
    median is a more reliable benchmark than mean for this selection.
    - **{top_district}** dominates listing volume, which is consistent with the EDA finding that 
    district is the strongest price driver across all segments.
    - Price and area show a positive correlation in the scatter plot, but the spread within each 
    tier suggests that **location premiums matter as much as size** in Cairo's market.
    """)