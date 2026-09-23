import streamlit as st
from source.oxylabs import scrape_details, search_comptitores,scraope_multiple_products
from source.database import DataBase

def scrape_and_store(asin,geo,domain):
    data=scrape_details(asin,geo,domain)
    db=DataBase()
    db.insert_product(data)
    return data

def fetch_and_store(origi_asin,geo,domain,pages=2):
    db=DataBase()
    parent =db.get_products(origi_asin)
    if not parent:
        return []
    search_domain=parent.get("amazon_domain", domain)
    search_geo=parent.get("amazon_geo", geo)
    st.write(f"using domain: {search_domain} | geo: {search_geo}")

    if parent.get("category"):
        search_cate=parent.get("category")
    if parent.get("category_path"):
        search_cate.extend(parent.get("category_path"))
    all_results=[]
    for category in search_cate[:4]:
        search_results=search_comptitores(query=parent["title"],domain=search_domain,pages=pages,category=search_cate,geo_location=geo)
        all_results.extend(search_results)
    compit_asin=list(set(r.get("asin") for r in all_results if r.get("asin") and r.get("asin")!=origi_asin))
    product_details=scraope_multiple_products(compit_asin[:30],domain,geo_location=search_geo)
    stored_cmp=[]
    for c in product_details:
        c["parent_asin"]=origi_asxin
        db.insert_product(c)
        stored_cmp.append(c)
    st.write(f"Comptitore summary")
    for comp in stored_cmp:
        price =comp.get("price","-")
        currency=comp.get("currency","-")
        if isinstance(price,(float,int)):
            price_str=f"{currency} {price:,.2f} if currency else {price:,.2f}"
        else:
            price_str=str(price)
        st.write(f"- {comp.get("title")- {price_str}} ")
    st.write("-------------------------------------------------------------------------------")

    return stored_cmp