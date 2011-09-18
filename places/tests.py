from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import GeoRoom, GRUser

class SimpleTest(TestCase):
    def test_new_gr(self):
        old_gr_len = len(GeoRoom.objects.all())
        old_gu_len = len(GRUser.objects.all())

        # call for a new georoom
        response = self.client.get(reverse('gr-new'))

        # check is created the room
        gr = GeoRoom.objects.all()
        self.assertEqual(len(gr), old_gr_len + 1)

        self.assertRedirects(response, reverse('gr', args=[gr[0].idx]))

        # and the user associated
        gu = GRUser.objects.all()
        self.assertEqual(len(gu), old_gu_len + 1)

    def test_404_gr(self):
        """
        If there isn't the geo room requested then throw a 404.
        """
        response = self.client.get(reverse('gr', args=["12345"]))
        self.failUnlessEqual(response.status_code, 404)

    def test_set_name_get(self):
        """
        Check that the GET method is not allowed here
        """
        response = self.client.get(reverse('gr-set-name'))
        self.failUnlessEqual(response.status_code, 405)

    def test_set_name(self):
        response = self.client.post(
                "/gr/name/", 
                '{"name": "miao"}',
                content_type="application/json")
        self.failUnlessEqual(response.status_code, 200)

    def test_marker(self):
        response = self.client.get(reverse('gr-marker', args=['pino']))
        self.failUnlessEqual(response.status_code, 200)
