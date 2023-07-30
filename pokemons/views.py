from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .models import Pokemon, PokemonAbility, PokemonStats, PokemonType
import re
import requests


def home(request):
    return HttpResponse("Gotta Catch 'Em All!")


def get_all_pokemons(request):
    return HttpResponse("This is the get_all_pokemons endpoint")


# HELPER FUNCTIONS


def get_pokemon_count() -> int:
    """
    Fetches the total count of Pokemon from the PokeAPI.

    Returns:
        int: The total count of Pokemon available in the PokeAPI.
    """
    count_url = "https://pokeapi.co/api/v2/pokemon"
    pokemon_count = requests.get(count_url).json()["count"]
    return pokemon_count


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
    """
    pokemon_count = get_pokemon_count()

    all_pokemons_url = f"https://pokeapi.co/api/v2/pokemon?limit={pokemon_count}"
    response = requests.get(all_pokemons_url)

    pokemon_ids = []

    results = response.json()["results"]
    for result in results:
        pokemon_id = extract_pokemon_id(result["url"])
        pokemon_ids.append(pokemon_id)
    return pokemon_ids


# VIEWS


class PokemonDataView(View):
    def update_or_create_record(self, request, pokemon_id) -> None:
        """
        Update or create a Pokemon record using data fetched from the PokeAPI.

        Parameters:
            pokemon_id (str): The pokemon ID from the pokemon url.
            request: Django HTTP request object.
        """
        pokemon_url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
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
                    pokemon_ability, _ = PokemonAbility.objects.update_or_create(
                        ability_name=ability_info["ability"]["name"],
                        defaults={"is_hidden": ability_info["is_hidden"]},
                        pokemon=pokemon,
                    )

                # Update Pokemon types
                for type_info in pokemon_data["types"]:
                    pokemon_type, _ = PokemonType.objects.update_or_create(
                        type_name=type_info["type"]["name"],
                        pokemon=pokemon,
                    )

                # Update Pokemon stats
                for stat_info in pokemon_data["stats"]:
                    pokemon_stat, _ = PokemonStats.objects.update_or_create(
                        base_stat_name=stat_info["stat"]["name"],
                        defaults={
                            "effort": stat_info["effort"],
                            "base_stat_num": stat_info["base_stat"],
                        },
                        pokemon=pokemon,
                    )

    def update_or_create_all(self, request) -> None:
        """
        Update or create Pokemon records for all available Pokemon using data fetched from the PokeAPI.

        Parameters:
            request: Django HTTP request object.
        """
        pokemons_ids = get_all_pokemon_ids(request)

        for pokemon_id in pokemons_ids:
            self.update_or_create_record(request, pokemon_id)

    def get(self, request):
        self.update_or_create_all(request)

        return JsonResponse({"message": "Data update successful."})
        # Can I have a button to get update
        # Need to redirect and maybe get a counter
        # Need to redirect when data is successful
