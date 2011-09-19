from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from .models import GeoRoom, GRUser

class SimpleTest(TestCase):
    fixtures = ['georoom.json',]
    def _get_post_from_georoom(self, url, gr_id, session_key, data={}):
        """
        Do an ajax POSTrequest from a georoom (emulating a browser)
        and return a response.
        """
        # this is needed in order to set the session_key correctly
        self.client.cookies[settings.SESSION_COOKIE_NAME] = session_key

        return self.client.post(
                url, 
                data,
                content_type="application/json",
                HTTP_REFERER=reverse('gr', args=[gr_id]))

    def test_new_gr(self):
        old_gr_len = len(GeoRoom.objects.all())
        old_gu_len = len(GRUser.objects.all())

        # call for a new georoom
        response = self.client.get(reverse('gr-new'))

        # check is created the room
        gr = GeoRoom.objects.all()
        self.assertEqual(len(gr), old_gr_len + 1)

        self.assertRedirects(response, reverse('gr', args=[gr[old_gr_len].idx]))

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
        name = "miao"
        session_key = 'e9aaa32313736c4093c7fe3fcba4ebd9'

        response = self._get_post_from_georoom(
                reverse('gr-set-name'),
                'GDill',
                session_key,
                '{"name": "%s"}' % name)

        self.failUnlessEqual(response.status_code, 200)
        gruser = GRUser.objects.get(session_key=session_key)
        self.failUnlessEqual(gruser.name, name)

    def test_set_name_without_session(self):
        name = "miao"
        session_key = 'miao'

        response = self._get_post_from_georoom(
                reverse('gr-set-name'),
                'GDill',
                session_key,
                '{"name": "%s"}' % name)

        self.failUnlessEqual(response.status_code, 400)

    def test_set_name_without_gr(self):
        name = "miao"
        session_key = 'e9aaa32313736c4093c7fe3fcba4ebd9'

        response = self._get_post_from_georoom(
                reverse('gr-set-name'),
                'geppo',
                session_key,
                '{"name": "%s"}' % name)

        self.failUnlessEqual(response.status_code, 400)

    def test_marker(self):
        response = self.client.get(reverse('gr-marker', args=['pino']))
        self.failUnlessEqual(response.status_code, 200)
