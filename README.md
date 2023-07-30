# Pokemon Crawler

A simple Pokemon API built on the Django Rest Framework.
This app interacts with the [PokeAPI](pokeapi.co) to fetch and store Pokemon data in a postgres database

## Endpoints

`/get-all-pokemons`: returns all pokemons names
`/pokemon/<pokemon_name>`: returns a pokemon's data
`/update-pokemon-data`: updates pokemons data from the [PokeAPI](pokeapi.co)

## Tables

`pokemons_pokemon`
`pokemons_pokemonability`
`pokemons_pokemontype`
`pokemons_pokemonstats`

## Getting started

Download [Docker Desktop](https://www.docker.com/products/docker-desktop/) for Mac or Windows. Docker Compose will be automatically installed.

**Start the server**: `docker-compose up`

**Install dependencies**: `docker-compose exec web python -m pip install -r requirements.txt`

**Run migration**:

- `docker-compose exec web python manage.py makemigrations pokemons`
- `docker-compose exec web python manage.py migrate`

**Connect to postgres**
`docker-compose exec db psql --username=postgres`

## Use the API

**Try these commands**:
`http GET http://0.0.0.0:8000/get-all-pokemons`
`http GET http://0.0.0.0:8000/pokemon/<pokemon_name>`
`http GET http GET http://0.0.0.0:8000/update-pokemon-data`

**Or Run the app**: [0.0.0.8000](0.0.0.8000)
`/get-all-pokemons`: returns all pokemons names
`/pokemon/<pokemon_name>`: returns a pokemon's data
`/update-pokemon-data`: updates pokemons data from [pokeapi.co](pokeapi.co) (logs indicate progress)

## Tests

Run tests: `docker-compose exec web python manage.py test pokemons`

## Explainer

WIP
