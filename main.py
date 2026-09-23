import streamlit as st

from source.database import DataBase
from source.oxylabs import scrape_details
from source.services import scrape_and_store, fetch_and_store
from source.database import DataBase

def render_header():
    st.title("Amazon Competitor Analyzer")
    st.caption("enter the ASIN of the product to get insights")


def render_inputs():
    asin = st.text_input("ASIN")
    geo = st.text_input("geo")
    domain = st.selectbox("domain", ["uk", "fr", "ae", "com", "it"])
    return asin, geo, domain


def render_product_card(product):
    with st.container():
        cols = st.columns([1, 2])
        images = product.get("images")
        if images and len(images) > 0:
            cols[0].image(images[0])
        else:
            cols[0].write("No images found")

        with cols[1]:
            st.subheader(product.get("title") or product.get("description") or "No description found")
            info_cols = st.columns(3)
            currency_val = product.get("currency")
            price = product.get("price")

            info_cols[0].metric("price", f"{currency_val}{price}" )
            info_cols[1].write(f"brand: {product.get('brand')}")
            info_cols[2].write(f"product: {product.get('product')}")

            # Fixed nested double-quotes using single-quotes inside
            dom_info = f"amazon.{product['domain']}"
            geo_info = product.get("geo")

            st.caption(f"domain: {dom_info} | geo: {geo_info}")
            st.write(product.get("url"))

            # Fixed nested double-quotes here as well
            if st.button("start analyzing competitors", key=f"analyze_{product['asin']}"):
                st.session_state["analyzing_asin"] = product["asin"]


def main():
    st.set_page_config(page_title="Amazon Competitor Analyzer",layout="wide")
    render_header()
    asin, geo, domain = render_inputs()

    if st.button("scraping"):
        if not asin.strip():
            st.error("Filling the ASIN field is mandatory!")
            st.markdown(
                """
                <style>
                div[data-baseweb="input"] {
                    border: 2px solid red !important;
                    border-radius: 4px;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
        else:
            with st.spinner("scraping the website..."):
                try:
                    st.write("scraping....")
                    result = scrape_and_store(asin, geo, domain)
                    render_product_card(result)
                    #st.write(result)
                    st.success("Done successfully")
                except Exception as e:
                    st.error(f"There was an error, please try again later: {e}")

    selected_asin = st.session_state.get("analyzing_asin")
    if selected_asin:
        st.divider()
        st.subheader(f"Amazon Competitor Analyzer for {selected_asin}")
        db = DataBase()
        existing_comp = db.search_products({"parent_asin": selected_asin})
        if not existing_comp:
            with st.spinner("searching competitors..."):
                comp = fetch_and_store(selected_asin, geo,domain)
            st.success("Done successfully")
        else:
            st.info(f"no compititors found")
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("refresh"):
                with st.spinner("refreshing..."):
                    comps = fetch_and_store(selected_asin, geo,domain)
                st.success(f"found{len(comps)} competitors")
        with col1:
            if st.button("analyze with LLM", type="primary"):
                with st.spinner("RUNING LLM ..."):
                    st.text("analysis")


if __name__ == "__main__":
    main()