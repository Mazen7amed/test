import plotly.express as px
import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import subprocess
import os
import stat

# Function to run bash commands
def run_bash_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode(), result.stderr.decode()
    except subprocess.CalledProcessError as e:
        return e.stdout.decode(), e.stderr.decode()

# Sidebar for Setup Environment
st.sidebar.title("Setup Environment")

if st.sidebar.button("Setup Environment"):
    with st.spinner("Installing Firefox and Geckodriver..."):
        
        # Install Firefox
        stdout, stderr = run_bash_command("apt-get update && apt-get install -y firefox-esr")
        if stderr:
            st.error(f"Error installing Firefox: {stderr}")
        else:
            st.success("Firefox installed successfully!")
        
        # Install Geckodriver
        stdout, stderr = run_bash_command(
            "curl -L https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz -o geckodriver.tar.gz && "
            "tar -xvzf geckodriver.tar.gz && "
            "mv geckodriver /usr/local/bin/ && rm geckodriver.tar.gz"
        )
        if stderr:
            st.error(f"Error installing Geckodriver: {stderr}")
        else:
            st.success("Geckodriver installed successfully!")

# Set up Geckodriver and Selenium
geckodriver_path = "/usr/local/bin/geckodriver"  # Default location after the bash setup
service = Service(executable_path=geckodriver_path)

def init_driver(service):
    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Run in headless mode
    firefox_options.binary_location = "/usr/bin/firefox"  # Ensure the binary path is correct
    driver = webdriver.Firefox(options=firefox_options, service=service)
    return driver

def scrape_jumia():
    try:
        driver = init_driver(service)
        driver.get("https://www.jumia.com.eg/")
        wait = WebDriverWait(driver, 10)
        click1 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".cls")))
        click1.click()
        search_box = driver.find_element(By.CSS_SELECTOR, "#fi-q")
        search_box.send_keys("smart watches")
        search_button = driver.find_element(By.CSS_SELECTOR, "button.-mls")
        search_button.click()
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 
            "div.-paxs.row._no-g._4cl-3cm-shs article.prd._fb.col.c-prd")))
        titles = driver.find_elements(By.CSS_SELECTOR, 
            "div.-paxs.row._no-g._4cl-3cm-shs article.prd._fb.col.c-prd")
        
        products_title = []
        products_cprice = []
        products_oprice = []
        products_dprice = []

        for title in titles:
            try:
                product_title = title.find_element(By.CSS_SELECTOR, "div.info h3.name").text
            except:
                product_title = "N/A"
            try:
                old_price = title.find_element(By.CSS_SELECTOR, "div.info div.s-prc-w div.old").text
            except:
                old_price = 0
            try:
                product_discount = title.find_element(By.CSS_SELECTOR, "div.info div.s-prc-w div.bdg._dsct._sm").text
            except:
                product_discount = 0
            current_price = title.find_element(By.CSS_SELECTOR, "div.info div.prc").text
            products_title.append(product_title)
            products_cprice.append(current_price)
            products_oprice.append(old_price)
            products_dprice.append(product_discount)
        
        driver.quit()
        df = pd.DataFrame({
            "Product Name": products_title,
            "Price": products_cprice,
            "Old Price": products_oprice,
            "Discount": products_dprice
        })
        return df

    except TimeoutException:
        st.error("Timeout occurred while trying to scrape data. Please try again later.")
        return pd.DataFrame()  # Return an empty DataFrame in case of an error

# Streamlit UI
st.title("Jumia Product Scraper")
st.subheader("We will scrape many products and choose the best product based on price and discount")

# Scrape Data
df = pd.DataFrame()  # Initialize an empty DataFrame
if st.button("Scrape Jumia Now"):
    with st.spinner("Scraping data from Jumia..."):
        df = scrape_jumia()

    if df.empty:
        st.warning("No data scraped. Please check the website or your scraping logic.")
    else:
        st.success("Scraping completed successfully!")
        st.dataframe(df)

# Sidebar Navigation
st.sidebar.title("Navigations")
st.sidebar.markdown("Created by [Youssef Shady](https://www.facebook.com/share/18MJH5gqat/?mibextid=LQQJ4d)")

# Data Exploration and Insights
if not df.empty:  # Ensure data is available before proceeding
    c1 = st.sidebar.selectbox("Select an option..", ["EDA", "Insights"])
    if c1 == "EDA":
        c2 = st.sidebar.radio("Select chart", ["Bar chart", "Scatter chart"])
        if c2 == "Scatter chart":
            st.subheader("Prices vs Old Prices")
            sc1 = px.scatter(df, x="Price", y="Old Price", color="Discount")
            st.plotly_chart(sc1)
            st.subheader("Discount vs Old Prices")
            sc2 = px.scatter(df, x="Old Price", y="Discount", color="Discount")
            st.plotly_chart(sc2)
        elif c2 == "Bar chart":
            st.subheader("Prices vs Old Prices")
            br1 = px.bar(df, x="Price", y="Old Price", color="Discount")
            st.plotly_chart(br1)
            st.subheader("Discount vs Old Prices")
            br2 = px.bar(df, x="Old Price", y="Discount", color="Discount")
            st.plotly_chart(br2)
    elif c1 == "Insights":
        st.subheader("""1) The comparison between the current price and the old price highlights the level of price reductions. A significant difference indicates a notable price drop, which could attract cost-conscious customers. Products with a large gap between the old and current price are more likely to appeal as value-for-money items. 2) Items with visible discounts and significant old price reductions are likely part of a sales strategy to clear inventory or promote specific products. Products with minimal price differences or no discounts may cater to premium segments or represent newly launched items.""")
