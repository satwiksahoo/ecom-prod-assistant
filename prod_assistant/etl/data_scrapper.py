# import csv
# import time
# import re
# import os
# from bs4 import BeautifulSoup
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains

# class FlipkartScraper:
#     def __init__(self, output_dir="data"):
#         self.output_dir = output_dir
#         os.makedirs(self.output_dir, exist_ok=True)

#     def get_top_reviews(self,product_url,count=2):
#         """Get the top reviews for a product.
#         """
#         options = uc.ChromeOptions()
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         driver = uc.Chrome(options=options,use_subprocess=True)

#         if not product_url.startswith("http"):
#             driver.quit()
#             return "No reviews found"

#         try:
#             driver.get(product_url)
#             time.sleep(4)
#             try:
#                 driver.find_element(By.XPATH, "//button[contains(text(), '✕')]").click()
#                 time.sleep(1)
#             except Exception as e:
#                 print(f"Error occurred while closing popup: {e}")

#             for _ in range(4):
#                 ActionChains(driver).send_keys(Keys.END).perform()
#                 time.sleep(1.5)

#             soup = BeautifulSoup(driver.page_source, "html.parser")
#             review_blocks = soup.select("div._27M-vq, div.col.EPCmJX, div._6K-7Co")
#             seen = set()
#             reviews = []

#             for block in review_blocks:
#                 text = block.get_text(separator=" ", strip=True)
#                 if text and text not in seen:
#                     reviews.append(text)
#                     seen.add(text)
#                 if len(reviews) >= count:
#                     break
#         except Exception:
#             reviews = []

#         driver.quit()
#         return " || ".join(reviews) if reviews else "No reviews found"
    
#     def scrape_flipkart_products(self, query, max_products=1, review_count=2):
#         """Scrape Flipkart products based on a search query.
#         """
#         options = uc.ChromeOptions()
#         driver = uc.Chrome(options=options,use_subprocess=True)
#         search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
#         driver.get(search_url)
#         time.sleep(4)

#         try:
#             driver.find_element(By.XPATH, "//button[contains(text(), '✕')]").click()
#         except Exception as e:
#             print(f"Error occurred while closing popup: {e}")

#         time.sleep(2)
#         products = []

#         items = driver.find_elements(By.CSS_SELECTOR, "div[data-id]")[:max_products]
#         for item in items:
#             try:
#                 title = item.find_element(By.CSS_SELECTOR, "div.KzDlHZ").text.strip()
#                 price = item.find_element(By.CSS_SELECTOR, "div.Nx9bqj").text.strip()
#                 rating = item.find_element(By.CSS_SELECTOR, "div.XQDdHH").text.strip()
#                 reviews_text = item.find_element(By.CSS_SELECTOR, "span.Wphh3N").text.strip()
#                 match = re.search(r"\d+(,\d+)?(?=\s+Reviews)", reviews_text)
#                 total_reviews = match.group(0) if match else "N/A"

#                 link_el = item.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
#                 href = link_el.get_attribute("href")
#                 product_link = href if href.startswith("http") else "https://www.flipkart.com" + href
#                 match = re.findall(r"/p/(itm[0-9A-Za-z]+)", href)
#                 product_id = match[0] if match else "N/A"
#             except Exception as e:
#                 print(f"Error occurred while processing item: {e}")
#                 continue

#             top_reviews = self.get_top_reviews(product_link, count=review_count) if "flipkart.com" in product_link else "Invalid product URL"
#             products.append([product_id, title, rating, total_reviews, price, top_reviews])

#         driver.quit()
#         return products
    
#     def save_to_csv(self, data, filename="product_reviews.csv"):
#         """Save the scraped product reviews to a CSV file."""
#         if os.path.isabs(filename):
#             path = filename
#         elif os.path.dirname(filename):  # filename includes subfolder like 'data/product_reviews.csv'
#             path = filename
#             os.makedirs(os.path.dirname(path), exist_ok=True)
#         else:
#             # plain filename like 'output.csv'
#             path = os.path.join(self.output_dir, filename)

#         with open(path, "w", newline="", encoding="utf-8") as f:
#             writer = csv.writer(f)
#             writer.writerow(["product_id", "product_title", "rating", "total_reviews", "price", "top_reviews"])
#             writer.writerows(data)
        
        
# import csv
# import os
# import time
# from bs4 import BeautifulSoup
# import undetected_chromedriver as uc

# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# import random
# time.sleep(random.uniform(2.5, 4.0))

# class FlipkartScraper:
#     def __init__(self, output_dir="data"):
#         self.output_dir = output_dir
#         os.makedirs(self.output_dir, exist_ok=True)

#     # -----------------------------
#     # Driver factory
#     # -----------------------------
#     # def _create_driver(self):
#     #     options = uc.ChromeOptions()
#     #     options.add_argument("--no-sandbox")
#     #     options.add_argument("--disable-blink-features=AutomationControlled")
#     #     # options.add_argument("--headless=new")  # enable later for deployment
#     #     return uc.Chrome(options=options, use_subprocess=True)
    
#     def _create_driver(self):
#         options = uc.ChromeOptions()
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-blink-features=AutomationControlled")

#         # FORCE MOBILE VIEW (CRITICAL)
#         options.add_argument(
#             "--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
#             "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 "
#             "Mobile/15E148 Safari/604.1"
#         )

#         options.add_argument("--window-size=390,844")

#         return uc.Chrome(options=options, use_subprocess=True)


#     # -----------------------------
#     # Close login popup safely
#     # -----------------------------
#     def _close_popup(self, driver):
#         try:
#             WebDriverWait(driver, 5).until(
#                 EC.element_to_be_clickable(
#                     (By.XPATH, "//button[contains(text(),'✕') or contains(text(),'✖')]")
#                 )
#             ).click()
#         except:
#             pass

#     # -----------------------------
#     # Extract reviews (same driver)
#     # -----------------------------
#     def _get_top_reviews(self, driver, product_url, count=2):
#         driver.get(product_url)
#         self._close_popup(driver)
#         time.sleep(3)

#         for _ in range(3):
#             ActionChains(driver).send_keys(Keys.END).perform()
#             time.sleep(1)

#         soup = BeautifulSoup(driver.page_source, "html.parser")
#         blocks = soup.select("div._27M-vq, div.col.EPCmJX, div._6K-7Co")

#         reviews, seen = [], set()
#         for block in blocks:
#             text = block.get_text(" ", strip=True)
#             if text and text not in seen:
#                 reviews.append(text)
#                 seen.add(text)
#             if len(reviews) >= count:
#                 break

#         return " || ".join(reviews) if reviews else "No reviews found"

#     # -----------------------------
#     # MAIN SCRAPER
#     # -----------------------------
#     def scrape_flipkart_products(self, query, max_products=1, review_count=2):
#         driver = self._create_driver()
#         products = []

#         try:
#             search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
#             driver.get(search_url)

#             self._close_popup(driver)

#             WebDriverWait(driver, 15).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-id]"))
#             )

#             items = driver.find_elements(By.CSS_SELECTOR, "div[data-id]")[:max_products]

#             for item in items:
#                 try:
#                     # TITLE (stable)
#                     # title = item.find_element(
#                     #     By.CSS_SELECTOR, "a[title]"
#                     # ).get_attribute("title")
                    
#                     link_el = item.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
#                     title = link_el.text.strip()

#                     price_el = item.find_elements(By.CSS_SELECTOR, "div._30jeq3")
#                     price = price_el[0].text if price_el else "N/A"

#                     rating_el = item.find_elements(By.CSS_SELECTOR, "div._3LWZlK")
#                     rating = rating_el[0].text if rating_el else "N/A"

#                     href = link_el.get_attribute("href")
#                     product_link = (
#                         href if href.startswith("http")
#                         else "https://www.flipkart.com" + href
#                     )


#                     # PRICE (text-based)
#                     price_el = item.find_elements(
#                         By.XPATH, ".//div[contains(text(),'₹')]"
#                     )
#                     price = price_el[0].text if price_el else "N/A"

#                     # RATING (known stable class)
#                     rating_el = item.find_elements(
#                         By.XPATH, ".//div[contains(@class,'_3LWZlK')]"
#                     )
#                     rating = rating_el[0].text if rating_el else "N/A"

#                     # PRODUCT LINK
#                     link_el = item.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
#                     href = link_el.get_attribute("href")
#                     product_link = (
#                         href if href.startswith("http")
#                         else "https://www.flipkart.com" + href
#                     )

#                     reviews = self._get_top_reviews(
#                         driver,
#                         product_link,
#                         review_count
#                     )

#                     products.append([
#                         title,
#                         rating,
#                         price,
#                         reviews
#                     ])

#                 except Exception as e:
#                     print("Item parse error:", e)

#         finally:
#             driver.quit()

#         return products

#     # -----------------------------
#     # CSV SAVE
#     # -----------------------------
#     def save_to_csv(self, data, filename="product_reviews.csv"):
#         if os.path.isabs(filename):
#             path = filename
#         elif os.path.dirname(filename):
#             path = filename
#             os.makedirs(os.path.dirname(path), exist_ok=True)
#         else:
#             path = os.path.join(self.output_dir, filename)

#         with open(path, "w", newline="", encoding="utf-8") as f:
#             writer = csv.writer(f)
#             writer.writerow(["title", "rating", "price", "top_reviews"])
#             writer.writerows(data)



# import csv
# import os
# import time
# import random
# from bs4 import BeautifulSoup
# import undetected_chromedriver as uc

# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC


# class AmazonScraper:
#     def __init__(self, output_dir="data"):
#         self.output_dir = output_dir
#         os.makedirs(self.output_dir, exist_ok=True)

#     # ---------------------------------
#     # Driver (desktop works fine for Amazon)
#     # ---------------------------------
#     def _create_driver(self):
#         options = uc.ChromeOptions()
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_argument("--disable-infobars")
#         options.add_argument("--disable-extensions")

#         options.add_argument(
#             "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
#             "AppleWebKit/537.36 (KHTML, like Gecko) "
#             "Chrome/121.0.0.0 Safari/537.36"
#         )

#         return uc.Chrome(options=options, use_subprocess=True)

#     # ---------------------------------
#     # Random delay (anti-bot)
#     # ---------------------------------
#     def _human_delay(self, a=2.0, b=4.0):
#         time.sleep(random.uniform(a, b))

#     # ---------------------------------
#     # Get top reviews from product page
#     # ---------------------------------
#     def _get_top_reviews(self, driver, product_url, count=2):
#         driver.get(product_url)
#         self._human_delay(2.5, 4.0)

#         soup = BeautifulSoup(driver.page_source, "html.parser")
#         review_blocks = soup.select("div[data-hook='review']")

#         reviews = []
#         for block in review_blocks:
#             text_el = block.select_one("span[data-hook='review-body']")
#             if text_el:
#                 reviews.append(text_el.get_text(" ", strip=True))
#             if len(reviews) >= count:
#                 break

#         return " || ".join(reviews) if reviews else "No reviews found"

#     # ---------------------------------
#     # MAIN SCRAPER
#     # ---------------------------------
#     def scrape_amazon_products(self, query, max_products=1, review_count=2):
#         driver = self._create_driver()
#         products = []

#         try:
#             search_url = (
#                 "https://www.amazon.in/s?k="
#                 + query.replace(" ", "+")
#             )
#             driver.get(search_url)

#             WebDriverWait(driver, 15).until(
#                 EC.presence_of_element_located(
#                     (By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
#                 )
#             )

#             self._human_delay()

#             items = driver.find_elements(
#                 By.CSS_SELECTOR, "div[data-component-type='s-search-result']"
#             )[:max_products]

#             for item in items:
#                 try:
#                     # TITLE
#                     title_el = item.find_element(By.CSS_SELECTOR, "h2 a span")
#                     title = title_el.text.strip()

#                     # PRODUCT LINK
#                     link_el = item.find_element(By.CSS_SELECTOR, "h2 a")
#                     product_link = link_el.get_attribute("href")

#                     # PRICE
#                     price_whole = item.find_elements(By.CSS_SELECTOR, "span.a-price-whole")
#                     price_frac = item.find_elements(By.CSS_SELECTOR, "span.a-price-fraction")
#                     if price_whole:
#                         price = price_whole[0].text.replace(",", "")
#                         if price_frac:
#                             price += "." + price_frac[0].text
#                         price = "₹" + price
#                     else:
#                         price = "N/A"

#                     # RATING
#                     rating_el = item.find_elements(By.CSS_SELECTOR, "span.a-icon-alt")
#                     rating = rating_el[0].text if rating_el else "N/A"

#                     # REVIEWS
#                     reviews = self._get_top_reviews(
#                         driver,
#                         product_link,
#                         review_count
#                     )

#                     products.append([
#                         title,
#                         rating,
#                         price,
#                         reviews
#                     ])

#                     self._human_delay(2.0, 3.5)

#                 except Exception as e:
#                     print("Item parse error:", e)

#         finally:
#             driver.quit()

#         return products

#     # ---------------------------------
#     # CSV SAVE
#     # ---------------------------------
#     def save_to_csv(self, data, filename="product_reviews.csv"):
#         if os.path.isabs(filename):
#             path = filename
#         elif os.path.dirname(filename):
#             path = filename
#             os.makedirs(os.path.dirname(path), exist_ok=True)
#         else:
#             path = os.path.join(self.output_dir, filename)

#         with open(path, "w", newline="", encoding="utf-8") as f:
#             writer = csv.writer(f)
#             writer.writerow(["title", "rating", "price", "top_reviews"])
#             writer.writerows(data)




# import csv
# import os
# import re
# import time
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, quote_plus


# class FlipkartScraper:
#     def __init__(self, output_dir="data"):
#         self.output_dir = output_dir
#         os.makedirs(self.output_dir, exist_ok=True)

#         self.headers = {
#             "User-Agent": (
#                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
#                 "AppleWebKit/537.36 (KHTML, like Gecko) "
#                 "Chrome/121.0.0.0 Safari/537.36"
#             ),
#             "Accept-Language": "en-IN,en;q=0.9",
#         }

#     # --------------------------------
#     # Fetch HTML safely
#     # --------------------------------
#     def _get_html(self, url):
#         res = requests.get(url, headers=self.headers, timeout=15)
#         res.raise_for_status()
#         return res.text

#     # --------------------------------
#     # Get top reviews (HTML only)
#     # --------------------------------
#     def get_top_reviews(self, product_url, count=2):
#         try:
#             html = self._get_html(product_url)
#             soup = BeautifulSoup(html, "lxml")

#             blocks = soup.select("div._27M-vq, div._6K-7Co")
#             reviews = []

#             for block in blocks:
#                 text = block.get_text(" ", strip=True)
#                 if text:
#                     reviews.append(text)
#                 if len(reviews) >= count:
#                     break

#             return " || ".join(reviews) if reviews else "No reviews found"

#         except Exception:
#             return "No reviews found"

#     # --------------------------------
#     # MAIN SEARCH SCRAPER
#     # --------------------------------
#     def scrape_flipkart_products(self, query, max_products=1, review_count=2):
#         products = []

#         search_url = (
#             "https://www.flipkart.com/search?q="
          
#             + quote_plus(query)
#         )

#         html = self._get_html(search_url)
#         soup = BeautifulSoup(html, "lxml")

#         items = soup.select("div[data-id]")[:max_products]

#         for item in items:
#             try:
#                 # TITLE
#                 title_el = item.select_one("div.KzDlHZ")
#                 title = title_el.get_text(strip=True) if title_el else "N/A"

#                 # PRICE
#                 price_el = item.select_one("div.Nx9bqj")
#                 price = price_el.get_text(strip=True) if price_el else "N/A"

#                 # RATING
#                 rating_el = item.select_one("div.XQDdHH")
#                 rating = rating_el.get_text(strip=True) if rating_el else "N/A"

#                 # TOTAL REVIEWS
#                 reviews_el = item.select_one("span.Wphh3N")
#                 reviews_text = reviews_el.get_text(strip=True) if reviews_el else ""
#                 match = re.search(r"\d+(,\d+)?(?=\s+Reviews)", reviews_text)
#                 total_reviews = match.group(0) if match else "N/A"

#                 # PRODUCT LINK
#                 link_el = item.select_one("a[href*='/p/']")
#                 href = link_el["href"]
#                 product_link = urljoin("https://www.flipkart.com", href)

#                 # PRODUCT ID
#                 pid_match = re.search(r"/p/(itm[0-9A-Za-z]+)", href)
#                 product_id = pid_match.group(1) if pid_match else "N/A"

#                 # REVIEWS
#                 top_reviews = self.get_top_reviews(
#                     product_link,
#                     count=review_count
#                 )

#                 products.append([
#                     product_id,
#                     title,
#                     rating,
#                     total_reviews,
#                     price,
#                     top_reviews
#                 ])

#                 time.sleep(1.5)  # polite delay

#             except Exception as e:
#                 print("Item parse error:", e)

#         return products

#     # --------------------------------
#     # SAVE CSV
#     # --------------------------------
#     def save_to_csv(self, data, filename="product_reviews.csv"):
#         if os.path.isabs(filename):
#             path = filename
#         elif os.path.dirname(filename):
#             path = filename
#             os.makedirs(os.path.dirname(path), exist_ok=True)
#         else:
#             path = os.path.join(self.output_dir, filename)

#         with open(path, "w", newline="", encoding="utf-8") as f:
#             writer = csv.writer(f)
#             writer.writerow([
#                 "product_id",
#                 "product_title",
#                 "rating",
#                 "total_reviews",
#                 "price",
#                 "top_reviews"
#             ])
#             writer.writerows(data)



# import csv
# import os
# import time
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import quote_plus

# import re 

# class AmazonScraper:
#     def __init__(self, output_dir="data"):
#         self.output_dir = output_dir
#         os.makedirs(self.output_dir, exist_ok=True)

#         self.headers = {
#             "User-Agent": (
#                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
#                 "AppleWebKit/537.36 (KHTML, like Gecko) "
#                 "Chrome/121.0.0.0 Safari/537.36"
#             ),
#             "Accept-Language": "en-IN,en;q=0.9",
#         }

#     # --------------------------------
#     # Fetch HTML
#     # --------------------------------
#     def _get_html(self, url):
#         res = requests.get(url, headers=self.headers, timeout=15)
#         res.raise_for_status()
#         return res.text

#     # --------------------------------
#     # Get top reviews (HTML)
#     # --------------------------------

    
    
#     def get_top_reviews(self, product_id, count=2):
#         try:
#             review_url = f"https://www.amazon.in/product-reviews/{product_id}"
#             html = self._get_html(review_url)
#             soup = BeautifulSoup(html, "lxml")

#             review_blocks = soup.select("div[data-hook='review']")
#             reviews = []

#             for block in review_blocks:
#                 body = block.select_one("span[data-hook='review-body']")
#                 if body:
#                     reviews.append(body.get_text(" ", strip=True))
#                 if len(reviews) >= count:
#                     break

#             return " || ".join(reviews) if reviews else "No reviews found"

#         except Exception:
#             return "No reviews found"


#     # --------------------------------
#     # MAIN SEARCH SCRAPER
#     # --------------------------------
#     def scrape_amazon_products(self, query, max_products=1, review_count=2):
#         products = []

#         search_url = (
#             "https://www.amazon.in/s?k="
#             + quote_plus(query)
#         )

#         html = self._get_html(search_url)
#         soup = BeautifulSoup(html, "lxml")

#         items = soup.select(
#             "div[data-component-type='s-search-result']"
#         )[:max_products]

#         for item in items:
#             try:
#                 # TITLE
#                 title_el = item.select_one("h2 a span")
#                 title = title_el.get_text(strip=True) if title_el else "N/A"

#                 # PRODUCT LINK
#                 link_el = item.select_one("h2 a")
#                 # product_link = (
#                 #     "https://www.amazon.in" + link_el["href"]
#                 #     if link_el and link_el.get("href")
#                 #     else "N/A"
#                 # )
                
#                 product_link = (
#                             "https://www.amazon.in" + link_el["href"]
#                             if link_el and link_el.get("href")
#                             else "N/A"
#                         )

#             # Extract ASIN (product_id)
#                 product_id = "N/A"
#                 if product_link != "N/A":
#                         match = re.search(r"/dp/([A-Z0-9]{10})", product_link)
#                         if not match:
#                             match = re.search(r"/gp/product/([A-Z0-9]{10})", product_link)
#                         if match:
#                             product_id = match.group(1)

#                 # PRICE
#                 price_whole = item.select_one("span.a-price-whole")
#                 price_frac = item.select_one("span.a-price-fraction")

#                 if price_whole:
#                     price = price_whole.get_text(strip=True).replace(",", "")
#                     if price_frac:
#                         price += "." + price_frac.get_text(strip=True)
#                     price = "₹" + price
#                 else:
#                     price = "N/A"

#                 # RATING
#                 rating_el = item.select_one("span.a-icon-alt")
#                 rating = rating_el.get_text(strip=True) if rating_el else "N/A"

#                 # TOTAL REVIEWS
#                 review_count_el = item.select_one(
#                     "span.a-size-base.s-underline-text"
#                 )
#                 total_reviews = (
#                     review_count_el.get_text(strip=True)
#                     if review_count_el else "N/A"
#                 )

#                 # TOP REVIEWS
#                 # top_reviews = (
#                 #     self.get_top_reviews(product_link, review_count)
#                 #     if product_link != "N/A"
#                 #     else "No reviews found"
#                 # )
                
#                 top_reviews = (
#                     self.get_top_reviews(product_id, review_count)
#                     if product_id != "N/A"
#                     else "No reviews found"
#                 )


#                 products.append([
#                     product_link.split("/dp/")[-1].split("/")[0]
#                     if "/dp/" in product_link else "N/A",
#                     title,
#                     rating,
#                     total_reviews,
#                     price,
#                     top_reviews
#                 ])

#                 time.sleep(1.5)  # polite delay

#             except Exception as e:
#                     print("Item parse error:", e)

#         return products

#     # --------------------------------
#     # SAVE CSV
#     # --------------------------------
#     def save_to_csv(self, data, filename="product_reviews.csv"):
#         if os.path.isabs(filename):
#             path = filename
#         elif os.path.dirname(filename):
#             path = filename
#             os.makedirs(os.path.dirname(path), exist_ok=True)
#         else:
#             path = os.path.join(self.output_dir, filename)

#         with open(path, "w", newline="", encoding="utf-8") as f:
#             writer = csv.writer(f)
#             writer.writerow([
#                 "product_id",
#                 "product_title",
#                 "rating",
#                 "total_reviews",
#                 "price",
#                 "top_reviews"
#             ])
#             writer.writerows(data)



import csv
import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus


class AmazonScraper:
    def __init__(self, output_dir="data"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-IN,en;q=0.9",
        }

    # --------------------------------
    # Fetch HTML
    # --------------------------------
    def _get_html(self, url):
        res = requests.get(url, headers=self.headers, timeout=15)
        res.raise_for_status()
        return BeautifulSoup(res.text, "lxml")

    # --------------------------------
    # Extract ASIN from URL
    # --------------------------------
    def _extract_asin(self, url):
        parts = url.split("/")
        for part in parts:
            if len(part) == 10 and part.isalnum():
                return part
        return "N/A"

    # --------------------------------
    # Scrape Reviews
    # --------------------------------
    def _scrape_reviews(self, asin, review_count):
        reviews = []
        if asin == "N/A":
            return reviews

        review_url = (
            f"https://www.amazon.in/product-reviews/{asin}"
            "?reviewerType=all_reviews"
        )

        soup = self._get_html(review_url)

        review_blocks = soup.select("div[data-hook='review']")

        for block in review_blocks[:review_count]:
            title = block.select_one("a[data-hook='review-title']")
            body = block.select_one("span[data-hook='review-body']")
            rating = block.select_one("i[data-hook='review-star-rating']")

            reviews.append({
                "title": title.get_text(strip=True) if title else "",
                "body": body.get_text(strip=True) if body else "",
                "rating": rating.get_text(strip=True) if rating else ""
            })

        return reviews

    # --------------------------------
    # Main Scraper
    # --------------------------------
    def scrape_amazon_products(self, query, max_products=1, review_count=2):
        encoded_query = quote_plus(query)
        search_url = f"https://www.amazon.in/s?k={encoded_query}"

        soup = self._get_html(search_url)

        products = soup.select("div[data-component-type='s-search-result']")
        results = []

        for product in products[:max_products]:
            title_el = product.select_one("h2 a span")
            link_el = product.select_one("h2 a")

            if not title_el or not link_el:
                continue

            title = title_el.get_text(strip=True)

            product_link = (
                "https://www.amazon.in" + link_el["href"]
                if link_el and link_el.get("href")
                else "N/A"
            )

            asin = self._extract_asin(product_link)

            reviews = self._scrape_reviews(asin, review_count)

            for review in reviews:
                results.append([
                    query,                  # search_query
                    title,                  # product_title
                    asin,                   # product_id
                    product_link,           # product_url
                    review["rating"],       # review_rating
                    review["title"],        # review_title
                    review["body"]          # review_text
                ])

            time.sleep(1.5)  # avoid blocking

        return results

    # --------------------------------
    # Save CSV
    # --------------------------------
    def save_to_csv(self, data, output_path):
        headers = [
            "search_query",
            "product_title",
            "product_id",
            "product_url",
            "review_rating",
            "review_title",
            "review_text",
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
