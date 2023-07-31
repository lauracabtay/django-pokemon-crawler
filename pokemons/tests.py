from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch
from .views import (
    GetAllPokemonsView,
)
from pokemons.models import Pokemon, PokemonAbility, PokemonStats, PokemonType


## UNIT TESTS


class TestGetAllPokemonsView(TestCase):
    @patch("pokemons.views.Pokemon.objects.values_list")
    def test_get_returns_sorted_pokemon_names(self, mock_values_list):
        mock_values_list.return_value = ["Bulbasaur", "Pikachu", "Ditto", "Charmander"]
        view = GetAllPokemonsView()
        response = view.get(None)
        expected_data = {
            "pokemon_names": ["Bulbasaur", "Charmander", "Ditto", "Pikachu"]
        }
        self.assertEqual(response.data, expected_data)
        self.assertEqual(response.status_code, 200)

        mock_values_list.assert_called_once_with("pokemon_name", flat=True)


## INTEGRATION TESTS


class TestPokemonViewsIntegration(TestCase):
    def setUp(self):
        # Set up test data in the database
        pokemon_bulbasaur = Pokemon.objects.create(
            pokemon_id=1,
            pokemon_name="Bulbasaur",
            height=7,
            weight=69,
            base_experience=64,
        )

        PokemonAbility.objects.create(
            ability_name="chlorophyll", is_hidden=False, pokemon=pokemon_bulbasaur
        )
        PokemonType.objects.create(type_name="grass", pokemon=pokemon_bulbasaur)
        PokemonStats.objects.create(
            base_stat_name="speed",
            effort=0,
            base_stat_num=45,
            pokemon=pokemon_bulbasaur,
        )

    def test_pokemon_details_success_view(self):
        client = APIClient()
        response = client.get("/pokemon/Bulbasaur")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "pokemon_id": 1,
                "pokemon_name": "Bulbasaur",
                "height": 7,
                "weight": 69,
                "base_experience": 64,
                "abilities": [{"ability_name": "chlorophyll", "is_hidden": False}],
                "types": [{"type_name": "grass"}],
                "stats": [
                    {"base_stat_name": "speed", "effort": 0, "base_stat_num": 45}
                ],
            },
        )

    def test_pokemon_details_not_found_view(self):
        client = APIClient()
        response = client.get("/pokemon/NonExistentPokemon")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.reason_phrase, "Not Found")

    def test_all_pokemons_view(self):
        client = APIClient()
        response = client.get("/all-pokemons")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_page_not_found_view(self):
        client = APIClient()
        response = client.get("/bad-page")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.reason_phrase, "Not Found")
