from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.chrome.options import Options
from ..models import ScrapedItems 

def scrape_internshala_jobs(user, keyword, pages=5):
    """
    Scrape Internshala jobs and save into DB (ScrapedItems).
    """

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    try:
        for page in range(1, pages + 1):
            url = f"https://internshala.com/jobs/keywords-{keyword}/page-{page}"
            driver.get(url)
            time.sleep(3)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            job_cards = soup.select("div.individual_internship.visibilityTrackerItem")
            # print(f"Internshala Page {page} URL: {url}")
            # print(f"Found {len(job_cards)} job cards")


            if not job_cards:
                break
            
            for i, card in enumerate(job_cards):
                # print(f"\n---- job card {i+1} --\n")
                
                try:
                    title_el = card.select_one("h3.job-internship-name a")
                    company_el = card.select_one("p.company-name")
                    location_el = card.select_one("p.locations")
                    salary_el = card.select_one(".row-1-item .desktop")
                    posted_on_el = card.select_one(".status-info span")
                    
                    profile_name = title_el.get_text(strip=True) if title_el else "N/A"
                    company_name = company_el.get_text(strip=True) if company_el else "N/A"
                    location_text = location_el.get_text(strip=True).replace(" ", "").replace("\n", "") if location_el else "N/A"
                    salary_text = salary_el.get_text(strip=True) if salary_el else "N/A"
                    posted_on = posted_on_el.get_text(strip=True) if posted_on_el else "N/A"
                    apply_link = "https://internshala.com" + card['data-href'] if card.has_attr('data-href') else None

                    if not (profile_name and company_name and apply_link):
                        continue
                    
                    try:
                        item = ScrapedItems.objects.create(
                        user=user,
                        profile=profile_name,
                        company=company_name,
                        experience="Anyone",  
                        location=location_text,
                        description=None,
                        apply_link=apply_link,
                        posted_on=posted_on
                    )
                        # print(f"profile : {item.profile} at {item.company} saved successfully.")
                    except Exception as e:
                        print(f"Error saving item: {e}")
                        continue

                except Exception as e:
                    print(f"an error occured: {e}")
                    continue

    finally:
        driver.quit()
