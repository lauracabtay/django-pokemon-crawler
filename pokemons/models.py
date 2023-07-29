from django.db import models


# Create your models here.
class Pokemon(models.Model):
    pokemon_id = models.IntegerField(primary_key=True)
    pokemon_name = models.CharField(max_length=50)
    height = models.IntegerField(null=True)
    weight = models.IntegerField(null=True)
    base_experience = models.IntegerField(null=True)

    objects = models.Manager()


class PokemonAbility(models.Model):
    ability_name = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(null=True)
    pokemon = models.ForeignKey(
        Pokemon, related_name="abilities", on_delete=models.CASCADE
    )

    objects = models.Manager()


class PokemonType(models.Model):
    type_name = models.CharField(max_length=50, null=True)
    pokemon = models.ForeignKey(Pokemon, related_name="types", on_delete=models.CASCADE)

    objects = models.Manager()


class PokemonStats(models.Model):
    base_stat_name = models.CharField(max_length=50, null=True)
    effort = models.IntegerField(null=True)
    base_stat_num = models.IntegerField(null=True)
    pokemon = models.ForeignKey(Pokemon, related_name="stats", on_delete=models.CASCADE)

    objects = models.Manager()
