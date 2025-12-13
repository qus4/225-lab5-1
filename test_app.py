import unittest
import requests

class TestApp(unittest.TestCase):

    def test_homepage(self):
        r = requests.get("http://10.48.229.142")  
        self.assertEqual(r.status_code, 200)
        self.assertIn("Contacts", r.text)

if __name__ == "__main__":
    unittest.main()
