import requests
import unittest

class TestFlaskApp(unittest.TestCase):

    BASE_URL = "http://flask-dev-service"   # service name inside Kubernetes

    def test_homepage_loads(self):
        """Homepage should return HTTP 200."""
        res = requests.get(self.BASE_URL)
        self.assertEqual(res.status_code, 200)

    def test_page_contains_title(self):
        """Homepage should contain the Contacts heading."""
        res = requests.get(self.BASE_URL)
        self.assertIn("Contacts", res.text)      # based on your HTML title

    def test_add_contact_form_exists(self):
        """Homepage should contain the Add Contact form."""
        res = requests.get(self.BASE_URL)
        self.assertIn("Add Contact", res.text)

if __name__ == "__main__":
    unittest.main()
