from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("", views.get_all_pokemons, name="get-all-pokemons"),
]
