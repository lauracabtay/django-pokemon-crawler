import logging
import requests
import re

from django.core.management.base import BaseCommand
from django.db import transaction
from requests.exceptions import HTTPError
from rest_framework.exceptions import APIException
from typing import List

from pokemons.models import Pokemon, PokemonAbility, PokemonStats, PokemonType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("logger")

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/pokemon"


class Command(BaseCommand):
    """Update or create Pokemon records using data from the PokeAPI."""

    def handle(self, *args, **kwargs) -> None:
        try:
            logger.info("Starting Pokemon data update")
            self.update_or_create_all()
            logger.info("Data update successful.")
        except HTTPError as err:
            raise APIException("Pokemon not found or API unavailable.") from err

    def update_or_create_all(self) -> None:
        """
        Update or create Pokemon records for all available Pokemon using data fetched from the PokeAPI.
        """
        pokemons_ids = self.get_all_pokemon_ids()
        pokemon_count = len(pokemons_ids)
        processed_pokemons = 0

        for pokemon_id in pokemons_ids:
            self.update_or_create_record(pokemon_id)
            processed_pokemons += 1

            if processed_pokemons % 20 == 0:
                logger.info(
                    f"{round((processed_pokemons/pokemon_count) * 100, 1)}% completed"
                )

    def update_or_create_record(self, pokemon_id) -> None:
        """
        Update or create a Pokemon record using data fetched from the PokeAPI.

        Parameters:
            pokemon_id (str): The pokemon ID from the pokemon url.
        """
        try:
            pokemon_url = f"{POKEAPI_BASE_URL}/{pokemon_id}"
            response = requests.get(pokemon_url)
            if response.status_code == 200:
                pokemon_data = response.json()

                with transaction.atomic():
                    pokemon, created = Pokemon.objects.update_or_create(
                        pokemon_id=pokemon_data["id"],
                        pokemon_name=pokemon_data["name"],
                        height=pokemon_data["height"],
                        weight=pokemon_data["weight"],
                        base_experience=pokemon_data["base_experience"],
                    )

                    # Update Pokemon abilities
                    for ability_info in pokemon_data["abilities"]:
                        _ = PokemonAbility.objects.update_or_create(
                            ability_name=ability_info["ability"]["name"],
                            defaults={"is_hidden": ability_info["is_hidden"]},
                            pokemon=pokemon,
                        )

                    # Update Pokemon types
                    for type_info in pokemon_data["types"]:
                        _ = PokemonType.objects.update_or_create(
                            type_name=type_info["type"]["name"],
                            pokemon=pokemon,
                        )

                    # Update Pokemon stats
                    for stat_info in pokemon_data["stats"]:
                        _ = PokemonStats.objects.update_or_create(
                            base_stat_name=stat_info["stat"]["name"],
                            defaults={
                                "effort": stat_info["effort"],
                                "base_stat_num": stat_info["base_stat"],
                            },
                            pokemon=pokemon,
                        )

        except HTTPError as err:
            raise APIException("Pokemon not found or API unavailable.") from err

        except ValueError as err:
            raise APIException(f"Unexpected response from PokeAPI: {err}") from err

    def get_all_pokemon_ids(self) -> List[str]:
        """
        Store all extracted pokemon IDs.

        Returns:
            A list of pokemon IDs.
        """
        try:
            count_url = POKEAPI_BASE_URL
            pokemon_count = requests.get(count_url).json()["count"]

            all_pokemons_url = f"{POKEAPI_BASE_URL}?limit={pokemon_count}"
            response = requests.get(all_pokemons_url)

            pokemon_ids = []

            results = response.json()["results"]
            for result in results:
                pokemon_id = self.extract_pokemon_id(result["url"])
                pokemon_ids.append(pokemon_id)
            return pokemon_ids
        except Exception as e:
            raise APIException(detail=f"Error fetching Pokemon data: {e}") from e

    def extract_pokemon_id(self, url) -> str:
        """
        Extracts the pokemon_id path parameter from the given pokemon URL.

        Parameters:
            url (str): The pokemon URL string from which to extract the pokemon_id.

        Returns:
            str: The extracted pokemon_id from the URL if found.
                If no path parameter is found, returns "No path parameter found".
        """
        pattern = r"/(\d+)/$"
        match = re.search(pattern, url)

        if match:
            return match.group(1)
        return "No Pokemon ID found"
