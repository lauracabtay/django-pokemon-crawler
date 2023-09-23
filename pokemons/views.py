from .models import Pokemon
from .serializers import PokemonSerializer
from rest_framework.exceptions import APIException
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView


class GetAllPokemonsView(APIView):
    """
    View for fetching a sorted list of all Pokemon names.
    """

    def get(self, request) -> Response:
        try:
            all_pokemon_names = Pokemon.objects.values_list("pokemon_name", flat=True)
            sorted_pokemon_names = sorted(all_pokemon_names, key=str)
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
