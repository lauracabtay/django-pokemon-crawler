from django.core.management import call_command
from celery import shared_task


@shared_task
def update_pokemon_data():
    """
    Celery task to update or create Pokemon records using data from the PokeAPI.
    """
    call_command("update_pokemon_data")
