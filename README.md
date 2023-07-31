# Pokemon Crawler

A simple Pokemon API built on the Django Rest Framework.
This app interacts with the [PokeAPI](pokeapi.co) to fetch and store Pokemon data in a postgres database.

## Getting started

Download [Docker Desktop](https://www.docker.com/products/docker-desktop/) for Mac or Windows. Docker Compose will be automatically installed.

**Start the server**:

- `docker-compose up`

**Install dependencies**:

- `docker-compose exec web python -m pip install -r requirements.txt`

**Run migration**:

- `docker-compose exec web python manage.py makemigrations pokemons`
- `docker-compose exec web python manage.py migrate`

To create or update pokemons:

- `docker-compose exec web python manage.py update-pokemon-data`

**Connect to postgres**

- `docker-compose exec db psql --username=postgres`

## Use the API

**Try these commands**:

- `http GET http://0.0.0.0:8000/all-pokemons`
- `http GET http://0.0.0.0:8000/pokemon/<pokemon_name>`

**Or Run the app**: [0.0.0.8000](0.0.0.8000)

- `/all-pokemons`: returns all pokemons names
- `/pokemon/<pokemon_name>`: returns a pokemon's data

## DB tables

- `pokemons_pokemon`
- `pokemons_pokemonability`
- `pokemons_pokemontype`
- `pokemons_pokemonstats`

## Tests

Run tests: `docker-compose exec web python manage.py test`

## Explainer

WIP
