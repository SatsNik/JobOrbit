from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.chrome.options import Options
from ..models import ScrapedItems

def scrap_linkedin(user, jobprofile, location):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    try:
        url = f"https://www.linkedin.com/jobs/search/?keywords={jobprofile}&location={location}"
        driver.get(url)
        time.sleep(5)
        i = 0
        while i < 5:  # Scroll 5 times to load more jobs
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            i += 1
            time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_cards = soup.find_all("div", class_="base-card")
        for card in job_cards:
            try:
                title_el = card.find("h3", class_="base-search-card__title")
                company_el = card.find("h4", class_="base-search-card__subtitle")
                experience_el = card.find("span", class_="job-search-card__experience")
                location_el = card.find("span", class_="job-search-card__location")
                posted_el = card.find("time", class_="job-search-card__listdate") or card.find("time", class_="job-search-card__listdate--new")
                link_el = card.find("a", class_="base-card__full-link")

                profile_name = title_el.get_text(strip=True) if title_el else None
                company_name = company_el.get_text(strip=True) if company_el else None
                location_text = location_el.get_text(strip=True) if location_el else ""
                posted_on = posted_el.get_text(strip=True) if posted_el else ""
                apply_link = link_el['href'] if link_el and link_el.has_attr('href') else None

                if not (profile_name and company_name and apply_link):
                    continue

                ScrapedItems.objects.create(
                    user=user,
                    profile=profile_name,
                    company=company_name,
                    experience=experience_el.get_text(strip=True) if experience_el else "Anyone",
                    location=location_text,
                    description=None,
                    apply_link=apply_link,
                    posted_on=posted_on
                )
            except Exception:
                # Skip malformed job cards
                continue
    finally:
        driver.quit()