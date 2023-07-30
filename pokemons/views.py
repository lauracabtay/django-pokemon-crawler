from .logger import logger
import re
import requests
from .models import Pokemon, PokemonAbility, PokemonStats, PokemonType
from .serializers import PokemonSerializer
from django.db import transaction
from requests.exceptions import HTTPError
from rest_framework.exceptions import APIException
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView


POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/pokemon"

# HELPER FUNCTIONS


def extract_pokemon_id(url) -> str:
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
        pokemon_id = match.group(1)
        return pokemon_id
    return "No pokemon ID found"


def get_all_pokemon_ids(request) -> list:
    """
    Store all extracted pokemon IDs.

    Parameters:
        request: Django HTTP request object.

    Returns:
        list: A list of all available Pokemon IDs.
    """
    try:
        pokemon_count = requests.get(POKEAPI_BASE_URL).json()["count"]
        response = requests.get(f"{POKEAPI_BASE_URL}?limit={pokemon_count}")

        pokemon_ids = []

        results = response.json()["results"]
        for result in results:
            pokemon_id = extract_pokemon_id(result["url"])
            pokemon_ids.append(pokemon_id)
        return pokemon_ids
    except Exception as e:
        raise APIException(detail=f"Error fetching Pokemon data: {e}") from e


# VIEWS


class PokemonUpdateDataView(APIView):
    """
    View for updating or creating Pokemon records using data from the PokeAPI.
    """

    def update_or_create_record(self, request, pokemon_id) -> None:
        """
        Update or create a Pokemon record using data fetched from the PokeAPI.

        Parameters:
            pokemon_id (str): The pokemon ID from the pokemon url.
            request: Django HTTP request object.
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

    def update_or_create_all(self, request) -> None:
        """
        Update or create Pokemon records for all available Pokemon using data fetched from the PokeAPI.

        Parameters:
            request: Django HTTP request object.
        """
        pokemons_ids = get_all_pokemon_ids(request)
        pokemon_count = len(pokemons_ids)
        processed_pokemons = 0

        for pokemon_id in pokemons_ids:
            self.update_or_create_record(request, pokemon_id)
            processed_pokemons += 1

            # Logs progress to server
            if processed_pokemons % 20 == 0:
                logger.info(
                    f"{round((processed_pokemons/pokemon_count) * 100, 1)}% completed"
                )

    def get(self, request) -> Response:
        """
        API endpoint for triggering the update of all Pokemon records.

        Parameters:
            request: Django HTTP request object.

        Returns:
            Response: A response indicating the success of the data update.
        """
        try:
            self.update_or_create_all(request)
            return Response({"message": "Data update successful."})
        except HTTPError as err:
            raise APIException("Pokemon not found or API unavailable.") from err


class GetAllPokemonsView(APIView):
    """
    View for fetching a sorted list of all Pokemon names.
    """

    def get(self, request) -> Response:
        try:
            all_pokemon_names = Pokemon.objects.values_list("pokemon_name", flat=True)
            sorted_pokemon_names = sorted(all_pokemon_names, key=str.casefold)
            return Response({"pokemon_names": sorted_pokemon_names})
        except Exception as err:
            raise APIException(
                "An error occurred while fetching Pokemon data."
            ) from err


class PokemonDetailsView(RetrieveAPIView):
    """
    View for fetching details of a specific Pokemon by name.
    """

    lookup_field = "pokemon_name"
    queryset = Pokemon.objects.all()
    serializer_class = PokemonSerializer
