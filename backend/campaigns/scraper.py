import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from .models import Campaign

def _get_driver():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    return webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=opts
    )


def parse_uah_integer(text: str) -> int:
    int_part = re.split(r"[.,]", text.strip())[0]
    digits_only = re.sub(r"\D", "", int_part)
    return int(digits_only) if digits_only else 0

def text_before_currency(el):
    raw = el.get_attribute('innerText') or ""
    return raw.split('₴')[0]


def scrape_monobank(campaign: Campaign, driver):
    driver.get(campaign.external_url)
    time.sleep(3)

    elems = driver.find_elements(By.CSS_SELECTOR, ".stats-data-value")
    if len(elems) >= 2:
        campaign.saved = parse_uah_integer(elems[0].get_attribute('innerText'))
        campaign.goal  = parse_uah_integer(elems[1].get_attribute('innerText'))

    name_el = driver.find_element(By.CSS_SELECTOR, "div.field.name > h1")
    campaign.name = name_el.text.strip()

    img_div = driver.find_element(By.CSS_SELECTOR, "#jar-state > div.img")
    style = img_div.get_attribute("style")
    m = re.search(r'url\("([^"]+)"\)', style)
    if m:
        campaign.image_url = m.group(1)

    campaign.save()

def scrape_prytulafoundation(campaign: Campaign, driver):
    driver.get(campaign.external_url)
    time.sleep(3)

    name_el = driver.find_element(By.CSS_SELECTOR, "h1.project__title")
    campaign.name = name_el.text.strip()

    saved_el = driver.find_element(By.CSS_SELECTOR, "div.number.first")
    campaign.saved = parse_uah_integer(text_before_currency(saved_el))

    goal_el = driver.find_element(By.CSS_SELECTOR, "p.number.second")
    campaign.goal = parse_uah_integer(goal_el.text)

    img_el = driver.find_element(
        By.CSS_SELECTOR,
        "div.richtext.project__description img"
    )
    campaign.image_url = img_el.get_attribute("src")

    campaign.save()

def scrape_privat24(campaign: Campaign, driver):
    driver.get(campaign.external_url)
    time.sleep(3)

    container = driver.find_element(By.CSS_SELECTOR, "div.sc-eldPxv.iJWUa-d")
    raw = container.text.strip()  
    parts = raw.split("/")
    if len(parts) == 2:
        campaign.saved = parse_uah_integer(parts[0])
        campaign.goal  = parse_uah_integer(parts[1])

    name_el = driver.find_element(
        By.CSS_SELECTOR,
        "div.sc-cPiKLX.ikEdsZ > div"
    )
    campaign.name = name_el.text.strip()

    img_url = None

    try:
        source = driver.find_element(
            By.CSS_SELECTOR,
            "picture > source[srcset]"
        )
        srcset = source.get_attribute("srcset")
        img_url = srcset.split()[0]
    except:
        pass

    if not img_url:
        try:
            img = driver.find_element(
                By.CSS_SELECTOR,
                "picture > img"
            )
            img_url = img.get_attribute("src")
        except:
            pass

    if not img_url:
        try:
            img = driver.find_element(
                By.CSS_SELECTOR,
                "div.sc-cPiKLX.jyaqOu img"
            )
            img_url = img.get_attribute("src")
        except:
            pass

    if img_url:
        campaign.image_url = img_url

    campaign.save()



def scrape_campaign(campaign: Campaign):
    driver = _get_driver()
    try:
        url = campaign.external_url.lower()
        if "monobank.ua" in url:
            scrape_monobank(campaign, driver)
        elif "prytulafoundation.org" in url:
            scrape_prytulafoundation(campaign, driver)
        elif "privat24.ua/env/donate" in url:
            scrape_privat24(campaign, driver)
        else:
            driver.get(campaign.external_url)
            time.sleep(3)
            site = campaign.site

            if site.selector_name:
                el = driver.find_element(By.CSS_SELECTOR, site.selector_name)
                campaign.name = el.text.strip()

            if site.selector_goal:
                el = driver.find_element(By.CSS_SELECTOR, site.selector_goal)
                campaign.goal = parse_uah_integer(el.text)

            if site.selector_saved:
                el = driver.find_element(By.CSS_SELECTOR, site.selector_saved)
                campaign.saved = parse_uah_integer(text_before_currency(el))

            if site.selector_image:
                el = driver.find_element(By.CSS_SELECTOR, site.selector_image)
                src = el.get_attribute("src") or el.get_attribute("style") or ""
                if "url(" in src:
                    m = re.search(r'url\("([^"]+)"\)', src)
                    src = m.group(1) if m else src
                campaign.image_url = src

            if "tviykrok.com.ua" in url:
                campaign.goal = campaign.saved + campaign.goal

            campaign.save()
    finally:
        driver.quit()
    return campaign


def scrape_saved_field(campaign: Campaign):
    driver = _get_driver()
    try:
        url = campaign.external_url.lower()
        if "monobank.ua" in url:
            scrape_monobank(campaign, driver)
        elif "prytulafoundation.org" in url:
            scrape_prytulafoundation(campaign, driver)
        elif "privat24.ua/env/donate" in url:
            scrape_privat24(campaign, driver)
        else:
            driver.get(campaign.external_url)
            time.sleep(3)
            site = campaign.site


            if site.selector_saved:
                el = driver.find_element(By.CSS_SELECTOR, site.selector_saved)
                campaign.saved = parse_uah_integer(text_before_currency(el))

            campaign.save()
    finally:
        driver.quit()