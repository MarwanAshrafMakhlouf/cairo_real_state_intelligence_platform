import streamlit as st


st.title("Welcome to the Cairo Real Estate Intelligence Platform")
st.subheader("A data driven look at Cairo real estate market")
st.write("""
        This platform analyzes 74,789 real estate listings scraped from 
    Cairo's major property platforms. Use it to explore pricing patterns, 
    compare districts, and estimate property values
""")
st.divider()
st.markdown("> Data reflects listing scraped in Q1 2026 and does not represent the full Caior market.")
st.divider()
st.write(
    "This platform is built around four tools — explore the Cairo "
    "real estate market through data visualizations, ask specific "
    "market questions, estimate a property price using machine learning, "
    "or chat directly with the data using the chatbot."
)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("**Market Overview**")
    st.write(""" Explore price distribution, district comparisons, and market segments""")
    if st.button("Open", key="overview"):
        st.switch_page("src/app/pages/overview.py")


with col2:
    st.markdown("**Market Explorer**")
    st.write("Answer specific questions about pricing, demand and amenties")
    if st.button("Open", key="explorer"):
        st.switch_page("src/app/pages/explorer.py")
with col3:
    st.markdown("**Price Estimator**")
    st.write("Get an estimated price estimate with confidence interval")
    if st.button("Open", key="estimator"):
        st.switch_page("src/app/pages/estimator.py")
with col4:
    st.markdown("**Market Chatbot**")
    st.write("Ask free-form questions about the Cairo market powered by RAG.")
    if st.button("Open", key="chatbot"):
        st.switch_page("src/app/pages/chatbot.py")
st.divider()
st.markdown("### About & Links")
st.caption("Built by Marwan Ashraf — Contact Info")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.link_button("LinkedIn", "https://www.linkedin.com/in/marwan-ashraf-9846a1202/", use_container_width=True)
with col2:
    st.link_button("GitHub", "https://github.com/MarwanAshrafMakhlouf?tab=repositories", use_container_width=True)
with col3:
    st.link_button("Portfolio", "https://marwanashrafmakhlouf.github.io/Portfolio/", use_container_width=True)
with col4:
    st.link_button("Source Code", "https://github.com/MarwanAshrafMakhlouf/cairo_real_state_intelligence_platform", use_container_width=True)
