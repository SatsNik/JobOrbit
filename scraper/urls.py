from django.urls import path
from .views import (
    login_view,
    register_view,
    verify_otp_view,
    logout_view,
    search_jobs_view,
    forgot_password_view,
    set_new_password_view,
    resend_otp_view,
)
urlpatterns = [
    path('', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('verify_otp/', verify_otp_view, name='verify_otp'),
    path('resend_otp/', resend_otp_view, name='resend_otp'),
    path('logout/', logout_view, name='logout'),
    path('search_jobs/', search_jobs_view, name='search_jobs'),
    path('forgot_password/', forgot_password_view, name='forgot_password'),
    path('set_new_password/', set_new_password_view, name='set_new_password'),
]