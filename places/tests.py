from django.test import TestCase
from django.core.urlresolvers import reverse


class SimpleTest(TestCase):
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
