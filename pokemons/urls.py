from django.urls import path
from .views import GetAllPokemonsView, PokemonUpdateDataView, PokemonDetailsView

urlpatterns = [
    path(
        "get-all-pokemons",
        GetAllPokemonsView.as_view(),
        name="get-all-pokemons",
    ),
    path(
        "update-pokemon-data",
        PokemonUpdateDataView.as_view(),
        name="update-pokemon-data",
    ),
    path(
        "pokemon/<str:pokemon_name>",
        PokemonDetailsView.as_view(),
        name="pokemon-details",
    ),
]
