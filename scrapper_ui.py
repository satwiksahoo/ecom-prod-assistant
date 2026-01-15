
# import streamlit as st
# from prod_assistant.etl.data_scrapper import FlipkartScraper
# from prod_assistant.etl.data_ingestion import DataIngestion
# import os

# flipkart_scraper = FlipkartScraper()
# output_path = "data/product_reviews.csv"
# st.title("📦 Product Review Scraper")

# if "product_inputs" not in st.session_state:
#     st.session_state.product_inputs = [""]

# def add_product_input():
#     st.session_state.product_inputs.append("")

# st.subheader("📝 Optional Product Description")
# product_description = st.text_area("Enter product description (used as an extra search keyword):")

# st.subheader("🛒 Product Names")
# updated_inputs = []
# for i, val in enumerate(st.session_state.product_inputs):
#     input_val = st.text_input(f"Product {i+1}", value=val, key=f"product_{i}")
#     updated_inputs.append(input_val)
# st.session_state.product_inputs = updated_inputs

# st.button("➕ Add Another Product", on_click=add_product_input)

# max_products = st.number_input("How many products per search?", min_value=1, max_value=10, value=1)
# review_count = st.number_input("How many reviews per product?", min_value=1, max_value=10, value=2)

# if st.button("🚀 Start Scraping"):
#     product_inputs = [p.strip() for p in st.session_state.product_inputs if p.strip()]
#     if product_description.strip():
#         product_inputs.append(product_description.strip())

#     if not product_inputs:
#         st.warning("⚠️ Please enter at least one product name or a product description.")
#     else:
#         final_data = []
#         for query in product_inputs:
#             st.write(f"🔍 Searching for: {query}")
#             results = flipkart_scraper.scrape_flipkart_products(query, max_products=max_products, review_count=review_count)
#             final_data.extend(results)

#         unique_products = {}
#         for row in final_data:
#             if row[1] not in unique_products:
#                 unique_products[row[1]] = row

#         final_data = list(unique_products.values())
#         st.session_state["scraped_data"] = final_data  # store in session
#         flipkart_scraper.save_to_csv(final_data, output_path)
#         st.success("✅ Data saved to `data/product_reviews.csv`")
#         st.download_button("📥 Download CSV", data=open(output_path, "rb"), file_name="product_reviews.csv")

# # This stays OUTSIDE "if st.button('Start Scraping')"
# if "scraped_data" in st.session_state and st.button("🧠 Store in Vector DB (AstraDB)"):
#     with st.spinner("📡 Initializing ingestion pipeline..."):
#         try:
#             ingestion = DataIngestion()
#             st.info("🚀 Running ingestion pipeline...")
#             ingestion.run_pipeline()
#             st.success("✅ Data successfully ingested to AstraDB!")
#         except Exception as e:
#             st.error("❌ Ingestion failed!")
#             st.exception(e)


# import streamlit as st
# # from prod_assistant.etl.data_scrapper import FlipkartScraper
# from prod_assistant.etl.data_ingestion import DataIngestion
# import os

# from prod_assistant.etl.data_scrapper import AmazonScraper


# # ------------------------------
# # Streamlit Page Config
# # ------------------------------
# st.set_page_config(
#     page_title="Ecommerce Product Scraper",
#     page_icon="📦",
#     layout="centered"
# )

# st.title("📦 Flipkart Product Review Scraper")

# OUTPUT_PATH = "data/product_reviews.csv"

# # ------------------------------
# # Session State Init
# # ------------------------------
# if "product_inputs" not in st.session_state:
#     st.session_state.product_inputs = [""]

# if "scraped_data" not in st.session_state:
#     st.session_state.scraped_data = None


# # ------------------------------
# # Helpers
# # ------------------------------
# def add_product_input():
#     st.session_state.product_inputs.append("")


# def reset_results():
#     st.session_state.scraped_data = None


# # ------------------------------
# # UI Inputs
# # ------------------------------
# st.subheader("📝 Optional Product Description")
# product_description = st.text_area(
#     "Used as an additional search keyword",
#     placeholder="e.g. best noise cancelling earbuds under 10k",
# )

# st.subheader("🛒 Product Names")

# updated_inputs = []
# for i, val in enumerate(st.session_state.product_inputs):
#     updated_inputs.append(
#         st.text_input(
#             f"Product {i + 1}",
#             value=val,
#             key=f"product_{i}",
#             on_change=reset_results
#         )
#     )

# st.session_state.product_inputs = updated_inputs

# st.button("➕ Add Another Product", on_click=add_product_input)

# col1, col2 = st.columns(2)
# with col1:
#     max_products = st.number_input(
#         "Products per search",
#         min_value=1,
#         max_value=10,
#         value=1
#     )

# with col2:
#     review_count = st.number_input(
#         "Reviews per product",
#         min_value=1,
#         max_value=10,
#         value=2
#     )

# st.divider()

# # ------------------------------
# # SCRAPE BUTTON
# # ------------------------------
# if st.button("🚀 Start Scraping", type="primary"):
#     product_inputs = [p.strip() for p in st.session_state.product_inputs if p.strip()]

#     if product_description.strip():
#         product_inputs.append(product_description.strip())

#     if not product_inputs:
#         st.warning("⚠️ Please enter at least one product or description.")
#     else:
#         # scraper = FlipkartScraper()
        
#         scraper = AmazonScraper()
#         final_data = []

#         with st.spinner("🔍 Scraping Flipkart..."):
#             for query in product_inputs:
#                 st.write(f"🔎 Searching for: **{query}**")
#                 try:
#                     # results = scraper.scrape_flipkart_products(
#                     #     query=query,
#                     #     max_products=max_products,
#                     #     review_count=review_count,
#                     # )
                    
#                     results = scraper.scrape_amazon_products(
#                         query=query,
#                         max_products=max_products,
#                         review_count=review_count
#                     )
#                     final_data.extend(results)
#                 except Exception as e:
#                     st.error(f"❌ Failed for query: {query}")
#                     st.exception(e)

#         if final_data:
#             # Deduplicate by product title (index 1)
#             unique = {}
#             for row in final_data:
#                 unique[row[1]] = row

#             final_data = list(unique.values())
#             st.session_state.scraped_data = final_data

#             scraper.save_to_csv(final_data, OUTPUT_PATH)

#             st.success("✅ Scraping completed and CSV saved!")
#         else:
#             st.warning("⚠️ No data scraped.")

# # ------------------------------
# # RESULTS + DOWNLOAD
# # ------------------------------
# if st.session_state.scraped_data:
#     st.subheader("📊 Scraped Products")

#     st.dataframe(
#         st.session_state.scraped_data,
#         use_container_width=True
#     )

#     with open(OUTPUT_PATH, "rb") as f:
#         st.download_button(
#             "📥 Download CSV",
#             data=f,
#             file_name="product_reviews.csv",
#             mime="text/csv"
#         )

# # ------------------------------
# # INGESTION BUTTON
# # ------------------------------
# if st.session_state.scraped_data:
#     st.divider()
#     if st.button("🧠 Store in Vector DB (AstraDB)"):
#         with st.spinner("📡 Running ingestion pipeline..."):
#             try:
#                 ingestion = DataIngestion()
#                 ingestion.run_pipeline()
#                 st.success("✅ Data successfully ingested into AstraDB!")
#             except Exception as e:
#                 st.error("❌ Ingestion failed")
#                 st.exception(e)



import streamlit as st
from prod_assistant.etl.data_scrapper import AmazonScraper
from prod_assistant.etl.data_ingestion import DataIngestion
import os

# ------------------------------
# Page Config
# ------------------------------
st.set_page_config(
    page_title="Amazon Product Review Scraper",
    page_icon="📦",
    layout="centered"
)

st.title("📦 Amazon Product Review Scraper")

OUTPUT_PATH = "data/product_reviews.csv"

# ------------------------------
# Session State Init
# ------------------------------
if "product_inputs" not in st.session_state:
    st.session_state.product_inputs = [""]

if "scraped_data" not in st.session_state:
    st.session_state.scraped_data = None

# ------------------------------
# Helpers
# ------------------------------
def add_product_input():
    st.session_state.product_inputs.append("")

def reset_results():
    st.session_state.scraped_data = None

# ------------------------------
# UI Inputs
# ------------------------------
st.subheader("📝 Optional Product Description")
product_description = st.text_area(
    "Used as an additional Amazon search keyword",
    placeholder="e.g. best noise cancelling headphones under 10000",
    on_change=reset_results
)

st.subheader("🛒 Product Names")

updated_inputs = []
for i, val in enumerate(st.session_state.product_inputs):
    updated_inputs.append(
        st.text_input(
            f"Product {i + 1}",
            value=val,
            key=f"product_{i}",
            on_change=reset_results
        )
    )

st.session_state.product_inputs = updated_inputs

st.button("➕ Add Another Product", on_click=add_product_input)

col1, col2 = st.columns(2)
with col1:
    max_products = st.number_input(
        "Products per search",
        min_value=1,
        max_value=10,
        value=1
    )

with col2:
    review_count = st.number_input(
        "Reviews per product",
        min_value=1,
        max_value=10,
        value=2
    )

st.divider()

# ------------------------------
# SCRAPE BUTTON
# ------------------------------
if st.button("🚀 Start Scraping", type="primary"):
    product_inputs = [p.strip() for p in st.session_state.product_inputs if p.strip()]

    if product_description.strip():
        product_inputs.append(product_description.strip())

    if not product_inputs:
        st.warning("⚠️ Please enter at least one product name or description.")
    else:
        scraper = AmazonScraper()
        final_data = []

        with st.spinner("🔍 Scraping Amazon..."):
            for query in product_inputs:
                st.write(f"🔎 Searching for: **{query}**")
                try:
                    results = scraper.scrape_amazon_products(
                        query=query,
                        max_products=max_products,
                        review_count=review_count
                    )
                    final_data.extend(results)
                except Exception as e:
                    st.error(f"❌ Failed for query: {query}")
                    st.exception(e)

        if final_data:
            # Deduplicate by product title (index 1)
            unique = {}
            for row in final_data:
                unique[row[1]] = row

            final_data = list(unique.values())
            st.session_state.scraped_data = final_data

            scraper.save_to_csv(final_data, OUTPUT_PATH)

            st.success("✅ Scraping completed and CSV saved!")
        else:
            st.warning("⚠️ No data scraped.")

# ------------------------------
# RESULTS + DOWNLOAD
# ------------------------------
if st.session_state.scraped_data:
    st.subheader("📊 Scraped Products")

    st.dataframe(
        st.session_state.scraped_data,
        use_container_width=True
    )

    with open(OUTPUT_PATH, "rb") as f:
        st.download_button(
            "📥 Download CSV",
            data=f,
            file_name="product_reviews.csv",
            mime="text/csv"
        )

# ------------------------------
# INGESTION BUTTON
# ------------------------------
if st.session_state.scraped_data:
    st.divider()
    if st.button("🧠 Store in Vector DB (AstraDB)"):
        with st.spinner("📡 Running ingestion pipeline..."):
            try:
                ingestion = DataIngestion()
                ingestion.run_pipeline()
                st.success("✅ Data successfully ingested into AstraDB!")
            except Exception as e:
                st.error("❌ Ingestion failed")
                st.exception(e)
