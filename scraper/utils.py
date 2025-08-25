from .models import ScrapedItems, EmailOTP
from django.conf import settings
from django.core.mail import send_mail
import random
from .scrapping.linkedin_scraper import scrap_linkedin 
from .scrapping.internshala_scraper import scrape_internshala_jobs

def jobsFinder(user, jobprofile, location):
    ScrapedItems.objects.filter(user=user).delete()
    scrap_linkedin(user, jobprofile, location)
    if location.lower() == "india":
        scrape_internshala_jobs(user, jobprofile)



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