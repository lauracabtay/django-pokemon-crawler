from django.urls import path
from .views import PokemonDataView

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("get-all-pokemons/", views.get_all_pokemons, name="get-all-pokemons"),
    path("update-pokemon-data/", PokemonDataView.as_view(), name="update-pokemon-data"),
]
