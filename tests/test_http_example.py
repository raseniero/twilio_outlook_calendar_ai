from HttpExample import main  # Import the main function
from dotenv import load_dotenv

import unittest
import azure.functions as func
import json
import os

load_dotenv()

class TestHttpExample(unittest.TestCase):
    def test_main_with_name(self):
        req = func.HttpRequest(
            method='GET',
            url='/api/HttpExample',
            body=b"",
            params={},
            headers={'Content-Type': 'application/json'}
        )
        resp = main(req)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('call_sid', resp.get_body().decode())

if __name__ == '__main__':
    unittest.main() 