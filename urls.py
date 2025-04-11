from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('history/', views.recipe_history, name='recipe_history'),
    path('documentation/',views.documentation,name='documentation'),
]