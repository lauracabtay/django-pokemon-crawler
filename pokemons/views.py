from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    return HttpResponse("Gotta Catch 'Em All!")


def get_all_pokemons(request):
    return HttpResponse("This is the get_all_pokemons endpoint")
