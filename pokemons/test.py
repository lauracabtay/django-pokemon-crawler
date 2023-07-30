from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import MagicMock, Mock, call, patch
from .views import (
    extract_pokemon_id,
    get_all_pokemon_ids,
    PokemonUpdateDataView,
    GetAllPokemonsView,
)
from pokemons.models import Pokemon, PokemonAbility, PokemonStats, PokemonType


## UNIT TESTS


class TestPokemonViews(TestCase):
    def test_extract_pokemon_id_with_valid_url(self):
        url = "https://pokeapi.co/api/v2/pokemon/25/"
        pokemon_id = extract_pokemon_id(url)
        self.assertEqual(pokemon_id, "25")

    def test_extract_pokemon_id_with_invalid_url(self):
        url = "https://pokeapi.co/api/v2/pokemon/"
        pokemon_id = extract_pokemon_id(url)
        self.assertEqual(pokemon_id, "No pokemon ID found")

    @patch("pokemons.views.requests.get")
    def test_get_all_pokemon_ids(self, mock_requests_get):
        # Mock the response from PokeAPI for get_pokemon_count()
        pokeapi_count_response = {"count": 3}

        mock_count_response = Mock()
        mock_count_response.json.return_value = pokeapi_count_response

        mock_requests_get.return_value = mock_count_response

        # Mock the response from PokeAPI for get_all_pokemon_ids()
        pokeapi_response = {
            "results": [
                {"url": "https://pokeapi.co/api/v2/pokemon/1/"},
                {"url": "https://pokeapi.co/api/v2/pokemon/2/"},
                {"url": "https://pokeapi.co/api/v2/pokemon/10/"},
            ]
        }

        mock_response = Mock()
        mock_response.json.return_value = pokeapi_response

        mock_requests_get.side_effect = [mock_count_response, mock_response]

        mock_request = Mock()
        results = get_all_pokemon_ids(mock_request)

        self.assertEqual(results, ["1", "2", "10"])


class TestPokemonUpdateDataView(TestCase):
    @patch("pokemons.views.requests.get")
    @patch("pokemons.views.Pokemon.objects.update_or_create")
    @patch("pokemons.views.PokemonAbility.objects.update_or_create")
    @patch("pokemons.views.PokemonType.objects.update_or_create")
    @patch("pokemons.views.PokemonStats.objects.update_or_create")
    def test_update_or_create_record(
        self,
        mock_stats_update_or_create,
        mock_type_update_or_create,
        mock_ability_update_or_create,
        mock_pokemon_update_or_create,
        mock_requests_get,
    ):
        # Mock the response from PokeAPI for a specific pokemon
        pokemon_id = "1"
        pokeapi_response = {
            "id": 1,
            "name": "bulbasaur",
            "height": 7,
            "weight": 69,
            "base_experience": 64,
            "abilities": [{"ability": {"name": "chlorophyll"}, "is_hidden": False}],
            "types": [{"type": {"name": "grass"}}],
            "stats": [{"stat": {"name": "speed"}, "effort": 0, "base_stat": 45}],
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = pokeapi_response

        mock_requests_get.return_value = mock_response

        mock_pokemon_object = MagicMock()
        mock_pokemon_update_or_create.return_value = (
            mock_pokemon_object,
            True,
        )  # The second value indicates that it was created

        view = PokemonUpdateDataView()
        view.update_or_create_record(MagicMock(), pokemon_id)

        mock_pokemon_update_or_create.assert_called_once_with(
            pokemon_id=pokeapi_response["id"],
            pokemon_name=pokeapi_response["name"],
            height=pokeapi_response["height"],
            weight=pokeapi_response["weight"],
            base_experience=pokeapi_response["base_experience"],
        )

        mock_ability_update_or_create.assert_called_once_with(
            ability_name=pokeapi_response["abilities"][0]["ability"]["name"],
            defaults={"is_hidden": pokeapi_response["abilities"][0]["is_hidden"]},
            pokemon=mock_pokemon_object,
        )

        mock_type_update_or_create.assert_called_once_with(
            type_name=pokeapi_response["types"][0]["type"]["name"],
            pokemon=mock_pokemon_object,
        )

        mock_stats_update_or_create.assert_called_once_with(
            base_stat_name=pokeapi_response["stats"][0]["stat"]["name"],
            defaults={
                "effort": pokeapi_response["stats"][0]["effort"],
                "base_stat_num": pokeapi_response["stats"][0]["base_stat"],
            },
            pokemon=mock_pokemon_object,
        )

    @patch("pokemons.views.get_all_pokemon_ids")
    @patch("pokemons.views.PokemonUpdateDataView.update_or_create_record")
    def test_update_or_create_all(
        self, mock_update_or_create_record, mock_get_all_pokemon_ids
    ):
        mock_pokemons_ids = ["1", "2", "3"]
        mock_get_all_pokemon_ids.return_value = mock_pokemons_ids

        mock_request = MagicMock()
        mock_pokemon_update_or_create_record = MagicMock()

        with patch.object(
            PokemonUpdateDataView,
            "update_or_create_record",
            mock_pokemon_update_or_create_record,
        ):
            view = PokemonUpdateDataView()
            view.update_or_create_all(mock_request)

        expected_calls = [
            call(mock_request, "1"),
            call(mock_request, "2"),
            call(mock_request, "3"),
        ]

        mock_pokemon_update_or_create_record.assert_has_calls(expected_calls)

    def test_get_calls_update_or_create_all_and_returns_response(self):
        view = PokemonUpdateDataView()
        view.update_or_create_all = mock_update_or_create_all = MagicMock()

        response = view.get(None)  # Pass a dummy request object
        mock_update_or_create_all.assert_called_once_with(None)

        self.assertEqual(response.data, {"message": "Data update successful."})
        self.assertEqual(response.status_code, 200)


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

    def test_get_all_pokemons_view(self):
        client = APIClient()
        response = client.get("/get-all-pokemons")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_page_not_found_view(self):
        client = APIClient()
        response = client.get("/bad-page")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.reason_phrase, "Not Found")
