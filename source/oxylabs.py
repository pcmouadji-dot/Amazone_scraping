import os
import json
import time
import streamlit as st
from  dotenv import load_dotenv
import requests

load_dotenv()

oxy_base_url="https://realtime.oxylabs.io/v1/queries"

def get_query(payload):
    username=os.getenv("OXY_USERNAME")
    password=os.getenv("OXY_PASSWORD")
    response=requests.post(oxy_base_url,json=payload,auth=(username,password))
    print("STATUS:", response.status_code)
    print("BODY:", response.text[:2000])
    response.raise_for_status()
    return response.json()
def normalize(content):
    category_path=[]
    if content.get("category_path"):
        category_path = [c in content.get("category_path") for c in content.get("category_path") if c]
    return {
        "asin": content.get("asin"),
        "url": content.get("url"),
        "brand": content.get("brand"),
        "price": content.get("price"),
        "stock": content.get("stock"),
        "title": content.get("title"),
        "rating": content.get("rating"),
        "images": content.get("images", []),
        "categories": content.get("category", []) or content.get("categories", []),
        "category_path": category_path,
        "currency": content.get("currency"),
        "buybox": content.get("buybox", [])
    }
def check_format(payload):
    if isinstance(payload, dict):
        if ("results" in payload) and isinstance(payload["results"],list) and payload["results"]:
            begin=payload["results"][0]
            if isinstance(begin,dict) and "content" in begin:
                return begin["content"]
        if "content" in payload:
            return payload.get("content")

    return payload
def scrape_details(asin,geo_location,domain):
    payload={
        "source":"amazon_product",
        "query":asin,
        "geo_location":geo_location,
        "domain":domain,
        "parse":True
    }
    raw=get_query(payload)
    raw1=check_format(raw)
    normalized=normalize(raw1)
    if not normalized.get("asin"):
        normalized["asin"]=asin
    normalized["geo_location"]=geo_location
    normalized["domain"]=domain
    return normalized

def normalized_search_results(item):
    asin=item["asin"] or item["product asin"]
    title=item["title"]
    return{
        "asin": asin,
        "title": title,
        "price": item["price"],
        "rating": item["rating"],
        "category": item["category"],
    }

def clean_title(title):
    if "-" in title:
        return title[:title.index("-")]
    if "|" in title:
        return title[:title.index("|")]
def extract_search_results(content):
    item=[]
    if not isinstance(content,dict):
        return item
    if "results" in content:
        results=content.get("results")
        if isinstance(results,dict):
            if "organic" in results:
                item.extend(results["organic"])
            if "paid" in results:
                item.extend(results["paid"])
    elif "product" in content and isinstance(content["product"],list):
        item.extend(content["product"])
    return item



def search_comptitores(query,categories,domain,geo_location="",pages=1):
    st.write("searching for comptitores")
    search_query=clean_title(query)
    strategies=["rating","price_asc","price_desc","featured"]
    results=[]
    procceced=set()

    for strategy in strategies:
        for page in range(1,pages+1):
            payload={
                "source":"amazon_product",
                "query":search_query,
                "domain":domain,
                "geo_location":geo_location,
                "sort_by":strategy,
                "page":page,
                "parse":True
            }
            if categories and categories[0]:
                payload["refinements"]={"categories": categories[0]}
            content=check_format(payload)
            items=extract_search_results(content)
            for item in items:
                result=normalized_search_results(item)
                if result and result["asin"] not in procceced:
                    procceced.add(result["asin"])
                    results.append(result)
    st.write(f"found {len(procceced)} comptitores")
    return results
def scraope_multiple_products(asins,geo_location,domain):
    products=[]
    progress_txt=st.empty()
    progress_bar=st.progress(0)
    total=len(asins)
    for idx,x in enumerate(asins):
        progress_bar.progress(idx/total)
        product=scrape_details(x,geo_location,domain)
        products.append(product)

        progress_txt.write(f"found:{product.get('title')}")
    progress_txt.empty()
    progress_bar.close()
    st.write(f"scraped  {len(products)} products out of {total} competitors")
    return products







