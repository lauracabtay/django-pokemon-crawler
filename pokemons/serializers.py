from collections import OrderedDict
from rest_framework import serializers
from .models import Pokemon, PokemonAbility, PokemonType, PokemonStats


class PokemonNameSerializer(serializers.Serializer):
    pokemon_name = serializers.CharField()


class PokemonAbilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PokemonAbility
        fields = ["ability_name", "is_hidden"]


class PokemonTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PokemonType
        fields = ["type_name"]


class PokemonStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PokemonStats
        fields = ["base_stat_name", "effort", "base_stat_num"]


class PokemonSerializer(serializers.ModelSerializer):
    abilities = PokemonAbilitySerializer(many=True)
    types = PokemonTypeSerializer(many=True)
    stats = PokemonStatsSerializer(many=True)

    class Meta:
        model = Pokemon
        fields = [
            "pokemon_id",
            "pokemon_name",
            "height",
            "weight",
            "base_experience",
            "abilities",
            "types",
            "stats",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        ordered_data = OrderedDict(
            [
                ("pokemon_id", data["pokemon_id"]),
                ("pokemon_name", data["pokemon_name"]),
                ("height", data["height"]),
                ("weight", data["weight"]),
                ("base_experience", data["base_experience"]),
                ("abilities", data["abilities"]),
                ("types", data["types"]),
                ("stats", data["stats"]),
            ]
        )
        return ordered_data
