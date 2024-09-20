from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# Initialize ChromeDriver with options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Function to scrape reviews
def scrape_amazon_reviews(product_url):
    driver.get(product_url)

    # List to store the scraped reviews
    reviews = []

    # Give the page some time to load
    time.sleep(10)

    # Scrape product name (use CSS selectors for Amazon)
    product_name = driver.find_element(By.ID, 'productTitle').text.strip()

    # Loop through pages of reviews
    while True:
        try:
            # Find all review elements on the page
            review_elements = driver.find_elements(By.CSS_SELECTOR, '.review')

            for review in review_elements:
                # Extract review details
                try:
                    rating_element = review.find_element(By.CSS_SELECTOR, '.review-rating span.a-icon-alt')
                    rating = rating_element.get_attribute('innerHTML').split(" ")[0]  # Extracts numeric rating
                except:
                    rating = "No rating"

                try:
                    title = review.find_element(By.CSS_SELECTOR, '.review-title').text
                except:
                    title = "No title"

                try:
                    body = review.find_element(By.CSS_SELECTOR, '.review-text-content').text.strip()
                except:
                    body = "No review body"

                try:
                    date = review.find_element(By.CSS_SELECTOR, '.review-date').text
                except:
                    date = "No date"

                reviews.append({
                    'product_name': product_name,
                    'rating': rating,
                    'title': title,
                    'body': body,
                    'date': date
                })

            # Try to find the next button and go to the next page
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//li[@class='a-last']/a"))
                )
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)  # Wait for the next page to load
            except:
                print("No 'Next' button found or reached the last page.")
                break  # No more pages, stop the loop

        except Exception as e:
            print("Error occurred: ", e)
            break

    return reviews

# Function to scrape product specifications
def scrape_amazon_specs(product_url):
    driver.get(product_url)

    # List to store product specifications
    specs = []

    # Give the page some time to load
    time.sleep(10)

    # Scrape product name
    product_name = driver.find_element(By.ID, 'productTitle').text.strip()

    try:
        # Locate the "Product details" section using the div with id="detailBullets_feature_div"
        product_details_section = driver.find_element(By.ID, 'detailBullets_feature_div')

        # Find all list items in the product details section
        detail_items = product_details_section.find_elements(By.CSS_SELECTOR, 'li')

        # Initialize an empty string to store all details as a single value
        product_details = ""

        # Loop through the list items and extract key-value pairs
        for item in detail_items:
            try:
                # Extract the label (bold text) and the corresponding value
                label = item.find_element(By.CSS_SELECTOR, 'span.a-text-bold').text.strip().replace("\n", "")
                value = item.find_elements(By.TAG_NAME, 'span')[-1].text.strip().replace("\n", "")
                product_details += f"{label}: {value}\n"
            except Exception as e:
                print("Error while extracting spec: ", e)

        # Save the entire product details as a single entry in the specs list
        specs.append({
            'product_name': product_name,
            'product_details': product_details.strip()  # Strip any trailing whitespace or newlines
        })

    except Exception as e:
        print(f"Error locating 'Product details' section for {product_name}: ", e)
        return None

    return specs


# URLs of the products reviews
product_urls = [
    "https://a.co/d/heiLJ8o",  # iHealth Track
    "https://a.co/d/7zamTnW",  # iHealth Neo
    "https://a.co/d/iQoYcgs"  # Oklar
]

# List to store all reviews from multiple products
all_reviews = []
# List to store all product specifications
all_specs = []

# Scrape reviews and specs for each product URL
for url in product_urls:
    print(f"Scraping reviews for product: {url}")
    product_reviews = scrape_amazon_reviews(url)
    all_reviews.extend(product_reviews)  # Add to the main list

    print(f"Scraping specs for product: {url}")
    product_specs = scrape_amazon_specs(url)
    if product_specs:
        all_specs.extend(product_specs)  # Add specs to the main list

# Convert reviews to DataFrame and save as CSV
df_reviews = pd.DataFrame(all_reviews)
df_reviews.to_csv('data/reviews.csv', index=False)

# Convert specs to DataFrame and save as CSV
# Convert specs to DataFrame and save as CSV
df_specs = pd.DataFrame(all_specs)
df_specs.to_csv('data/specs.csv', index=False)

# Close the driver
driver.quit()
