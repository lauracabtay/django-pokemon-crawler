from django.urls import path
from .views import GetAllPokemonsView, PokemonDetailsView

urlpatterns = [
    path(
        "all-pokemons",
        GetAllPokemonsView.as_view(),
        name="all-pokemons",
    ),
    path(
        "pokemon/<str:pokemon_name>",
        PokemonDetailsView.as_view(),
        name="pokemon-details",
    ),
]
