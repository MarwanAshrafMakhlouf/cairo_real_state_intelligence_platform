import streamlit as st


def apply_sidebar_filters(df, locations):
    
    st.markdown("### Filters")

    # --- Property Type ---
    st.markdown("**Property type**")
    property_types = {"Apartment": "apartments", "Villa": "villas"}
    selected_type = st.radio("", list(property_types.keys()), 
                                      horizontal=True, label_visibility="collapsed")
    selected_type_df = property_types[selected_type]

    # --- Property Subtype ---
    subtype_map = {
        "Apartment": ["Apartment", "Duplex", "Studio", "Penthouse", "Roof", "Hotel Apartment", "Room"],
        "Villa": ["Town House", "Stand Alone Villa", "Twin House", "iVilla"]
    }
    selected_subtypes = st.multiselect("Property subtype", 
                                                subtype_map[selected_type], 
                                                default=subtype_map[selected_type])

    # --- Transaction ---
    st.markdown("**Transaction**")
    selected_transaction = st.radio("", ["Sale", "Rent"], 
                                             horizontal=True, label_visibility="collapsed")

    # --- Rental Frequency ---
    selected_frequencies = None
    if selected_transaction == "Rent":
        selected_frequencies = st.multiselect("Rental frequency",
                                                       ["daily", "weekly", "monthly", "yearly"],
                                                       default=["monthly", "yearly"])

    # --- Location ---
    st.markdown("**Location**")
    district_options = ["All"] + list(locations.keys())
    selected_district = st.selectbox("District", district_options)

    selected_area = "All"
    selected_neighborhood = "All"

    if selected_district != "All":
        area_options = ["All"] + sorted(locations[selected_district].keys())
        selected_area = st.selectbox("Area", area_options)

        if selected_area != "All":
            neighborhood_options = locations[selected_district][selected_area]
            if neighborhood_options:
                selected_neighborhood = st.selectbox("Neighborhood", 
                                                              ["All"] + sorted(neighborhood_options))

    # --- Price Range ---
    filtered_df = df[
        (df["property_type"] == selected_type_df) &
        (df["sale_or_rent"].str.lower() == selected_transaction.lower())
    ]

    price_99 = filtered_df["price"].quantile(0.99)

    filtered_for_price = filtered_df[filtered_df["price"] <= price_99]["price"].dropna()

    median_for_outlier = filtered_df[filtered_df["price"] >= price_99]["price"].median()

    price_min = int(filtered_for_price.min()) if not filtered_for_price.empty else 0
    price_max = int(filtered_for_price.max()) if not filtered_for_price.empty else 10_000_000

    st.markdown("**Price range (EGP)**")
    selected_price = st.slider("", price_min, price_max, (price_min, price_max),
                                        step=50_000, label_visibility="collapsed")

    # --- Area m² ---
    area_vals = df[df["area (m²)"] <= df["area (m²)"].quantile(0.99)]["area (m²)"].dropna()
    selected_area_m2 = st.slider("Area (m²)", 
                                          int(area_vals.min()), int(area_vals.max()),
                                          (int(area_vals.min()), int(area_vals.max())),
                                          step=10)

    # --- Bedrooms ---
    st.markdown("**Bedrooms**")
    selected_bedrooms = st.multiselect("", ["Any", "1", "2", "3", "4+"], 
                                                default=["Any"],
                                                label_visibility="collapsed")
    if not selected_bedrooms or "Any" in selected_bedrooms:
        selected_bedrooms = None

    # --- Furnished ---
    st.markdown("**Furnished**")
    furnished_choice = st.radio("", ["All", "Yes", "No"], 
                                         horizontal=True, label_visibility="collapsed")

    # --- Completion Status ---
    st.markdown("**Completion status**")
    completion_choice = st.radio("", ["All", "Ready", "Off-plan"], 
                                          horizontal=True, label_visibility="collapsed")

    # --- Floor Level ---
    selected_levels = None
    if selected_type == "Apartment":
        all_levels = sorted(df["level_clean"].dropna().unique().tolist())
        selected_levels = st.multiselect("Floor level", all_levels)

    # --- Reset ---
    st.markdown("---")
    if st.button("Reset filters", use_container_width=True):
        st.rerun()

    # ── Apply filters ──────────────────────────────────────────────
    filtered = df.copy()

    filtered = filtered[filtered["property_type"] == selected_type_df]
    filtered = filtered[filtered["property_subtype"].isin(selected_subtypes)]
    filtered = filtered[filtered["sale_or_rent"].str.lower() == selected_transaction.lower()]

    if selected_transaction == "Rent" and selected_frequencies:
        filtered = filtered[filtered["rental frequency"].isin(selected_frequencies)]

    if selected_district != "All":
        filtered = filtered[filtered["district"] == selected_district]
    if selected_area != "All":
        filtered = filtered[filtered["area"] == selected_area]
    if selected_neighborhood != "All":
        filtered = filtered[filtered["neighborhood"] == selected_neighborhood]

    filtered = filtered[
        (filtered["price"] >= selected_price[0]) &
        (filtered["price"] <= selected_price[1])
    ]
    filtered = filtered[
        (filtered["area (m²)"] >= selected_area_m2[0]) &
        (filtered["area (m²)"] <= selected_area_m2[1])
    ]

    if selected_bedrooms:
        if "4+" in selected_bedrooms:
            filtered = filtered[
                (filtered["bedrooms"].isin([int(b) for b in selected_bedrooms if b != "4+"])) |
                (filtered["bedrooms"] >= 4)
            ]
        else:
            filtered = filtered[filtered["bedrooms"].isin([int(b) for b in selected_bedrooms])]

    if furnished_choice != "All":
        filtered = filtered[filtered["furnished"].str.lower() == furnished_choice.lower()]

    if completion_choice != "All":
        completion_map = {"Ready": "ready", "Off-plan": "off-plan"}
        filtered = filtered[filtered["completion status"] == completion_map[completion_choice]]

    if selected_levels and selected_type=="Apartment":
        filtered = filtered[filtered["level_clean"].isin(selected_levels)]

    return filtered, selected_type, selected_transaction, median_for_outlier