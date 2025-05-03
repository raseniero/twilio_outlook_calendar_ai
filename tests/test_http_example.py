import unittest
import azure.functions as func
from HttpExample import main  # Import the main function

class TestHttpExample(unittest.TestCase):
    def test_main_with_name(self):
        req = func.HttpRequest(
            method='GET',
            url='/api/HttpExample',
            body=b"",
            params={'name': 'Jairo'}
        )
        resp = main(req)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Hello, Jairo', resp.get_body().decode())

    def test_main_without_name(self):
        req = func.HttpRequest(
            method='GET',
            url='/api/HttpExample',
            body=b"",
            params={}
        )
        resp = main(req)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('Please pass a name', resp.get_body().decode())

if __name__ == '__main__':
    unittest.main() 