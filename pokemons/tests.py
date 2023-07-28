from django.test import TestCase
from django.urls import reverse


# Integration test
class ViewsTestCase(TestCase):
    def test_home_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gotta Catch 'Em All!")

    def test_get_all_view(self):
        response = self.client.get(reverse("get-all-pokemons"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This is the get_all_pokemons endpoint")
