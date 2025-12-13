import requests
import unittest

class TestFlaskApp(unittest.TestCase):

    BASE_URL = "http://flask-dev-service"   # Kubernetes DNS for DEV

    def test_homepage_loads(self):
        """Check homepage returns HTTP 200."""
        res = requests.get(self.BASE_URL)
        self.assertEqual(res.status_code, 200)

    def test_page_contains_title(self):
        """Check homepage contains expected title."""
        res = requests.get(self.BASE_URL)
        self.assertIn("Contacts", res.text)

    def test_add_contact_form_exists(self):
        """Check Add Contact form exists on the page."""
        res = requests.get(self.BASE_URL)
        self.assertIn("Add Contact", res.text)

if __name__ == "__main__":
    unittest.main()
