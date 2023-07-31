from django.test import TestCase
from requests.exceptions import HTTPError
from rest_framework.exceptions import APIException
from unittest.mock import MagicMock, call, patch

from app.management.commands.update_pokemon_data import Command
from pokemons.models import Pokemon, PokemonAbility, PokemonStats, PokemonType


class TestUpdatePokemonData(TestCase):
    @patch("app.management.commands.update_pokemon_data.Command.extract_pokemon_id")
    def test_extract_pokemon_id_with_valid_url(self, mock_extract_pokemon_id):
        url = "https://pokeapi.co/api/v2/pokemon/25/"
        mock_extract_pokemon_id.return_value = "25"

        command = Command()
        pokemon_id = command.extract_pokemon_id(url)

        self.assertEqual(pokemon_id, "25")

    @patch("app.management.commands.update_pokemon_data.Command.extract_pokemon_id")
    def test_extract_pokemon_id_with_invalid_url(self, mock_extract_pokemon_id):
        url = "https://pokeapi.co/api/v2/pokemon/"
        mock_extract_pokemon_id.return_value = "oh-no"
        command = Command()

        pokemon_id = command.extract_pokemon_id(url)

        self.assertEqual(pokemon_id, "oh-no")

    @patch("app.management.commands.update_pokemon_data.requests.get")
    def test_get_all_pokemon_ids(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "count": 3,
            "results": [
                {"url": "https://pokeapi.co/api/v2/pokemon/1/"},
                {"url": "https://pokeapi.co/api/v2/pokemon/2/"},
                {"url": "https://pokeapi.co/api/v2/pokemon/3/"},
            ],
        }
        mock_get.return_value = mock_response

        command = Command()
        pokemon_ids = command.get_all_pokemon_ids()

        self.assertEqual(pokemon_ids, ["1", "2", "3"])

    @patch("app.management.commands.update_pokemon_data.requests.get")
    def test_update_or_create_record_success(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_pokemon_data = {
            "id": 1,
            "name": "bulbasaur",
            "height": 7,
            "weight": 69,
            "base_experience": 64,
            "abilities": [{"ability": {"name": "overgrow"}, "is_hidden": False}],
            "types": [{"type": {"name": "grass"}}],
            "stats": [{"stat": {"name": "hp"}, "effort": 0, "base_stat": 45}],
        }
        mock_response.json.return_value = mock_pokemon_data
        mock_requests_get.return_value = mock_response

        command = Command()
        command.update_or_create_record(1)
        pokemon = Pokemon.objects.get(pokemon_id=1)

        self.assertEqual(pokemon.pokemon_name, "bulbasaur")
        self.assertTrue(PokemonAbility.objects.filter(pokemon=pokemon).exists())
        self.assertTrue(PokemonStats.objects.filter(pokemon=pokemon).exists())
        self.assertTrue(PokemonType.objects.filter(pokemon=pokemon).exists())

    @patch("app.management.commands.update_pokemon_data.Command.get_all_pokemon_ids")
    @patch(
        "app.management.commands.update_pokemon_data.Command.update_or_create_record"
    )
    def test_update_or_create_all(
        self, mock_update_or_create_record, mock_get_all_pokemon_ids
    ):
        mock_get_all_pokemon_ids.return_value = ["1", "2", "3"]

        command = Command()
        command.update_or_create_all()

        mock_update_or_create_record.assert_any_call("1")
        mock_update_or_create_record.assert_any_call("2")
        mock_update_or_create_record.assert_any_call("3")

    @patch("app.management.commands.update_pokemon_data.Command.update_or_create_all")
    @patch("logging.Logger.info")
    def test_handle_successful(self, mock_logger_info, mock_update_or_create_all):
        command = Command()
        command.handle()

        expected_calls = [
            call("Starting Pokemon data update"),
            call("Data update successful."),
        ]

        mock_logger_info.assert_has_calls(expected_calls)
        mock_update_or_create_all.assert_called_once()
