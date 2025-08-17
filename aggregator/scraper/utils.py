from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.chrome.options import Options
from .models import ScrapedItems, EmailOTP
from django.conf import settings
from django.core.mail import send_mail
import random

def jobsFinder(user, jobprofile, location):
    ScrapedItems.objects.filter(user=user).delete()
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    try:
        url = f"https://www.linkedin.com/jobs/search/?keywords={jobprofile}&location={location}"
        driver.get(url)
        time.sleep(5)
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
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
                    posted_on=posted_on,
                    source="LinkedIn"
                )
            except Exception:
                # Skip malformed job cards
                continue
    finally:
        driver.quit()


def send_otp(user):
    """
    Generates and emails a new OTP to the given user.
    Ensures only the latest OTP is valid by marking all previous unused OTPs as used.
    """
    # Invalidate any previous, unused OTPs for this user
    EmailOTP.objects.filter(user=user, is_used=False).update(is_used=True)

    otp = str(random.randint(100000, 999999))
    EmailOTP.objects.create(user=user, otp=otp)

    send_mail(
        subject="JobOrbit Account Verification",
        message=f'''Hello dear,
Thank you for choosing JobOrbit, All jobs at ONE place.
Your OTP is: {otp}, please complete your account verification.
        ''',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return otp