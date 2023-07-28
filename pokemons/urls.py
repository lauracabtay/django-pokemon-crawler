from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("get-all-pokemons/", views.get_all_pokemons, name="get-all-pokemons"),
]
