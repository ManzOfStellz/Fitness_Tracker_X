from django.urls import path
from .views import home, profile, RegisterView, calories, exercises, calorie_history, download_data
from django.contrib import admin

#my url paths for the functionality of the application
#I have added a path for the home page, profile page, register page, admin page, calories page and exercise page
#I have also added a path for the calorie history (graphs) page and the download data page


urlpatterns = [
    path('', home, name='users-home'),
    path('register/', RegisterView.as_view(), name='users-register'),
    path('profile/', profile, name='users-profile'),
    path('calories/', calories, name='calories'),
    path('exercise/', exercises, name='exercise'),
    path('calorie_history/', calorie_history, name='calorie_history'),
    path('request_data/', download_data, name='req')
]