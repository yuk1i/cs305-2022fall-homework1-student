import random
import string
import unittest
import requests
import tests.BasicTest
import requests
import os


class TestTask5Cookie(tests.BasicTest.BasicTest):
    def test02TestGetImage(self):
        s = requests.session()
        resp = s.get(self.server_base + "api/getimage")
        self.assertEqual(resp.status_code, 403)

        resp = s.post(self.server_base + "api/login", json={"username": "admin", "password": "admin"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.cookies.get("Authenticated"), "yes")

        resp = s.get(self.server_base + "api/getimage")
        self.assertEqual(resp.status_code, 200)
        flen = self.assertFileContentEqual('data/test.jpg', resp.content)
        self.assertEqual(int(resp.headers['Content-Length']), flen)
        self.assertIn(resp.headers['Content-Type'], ['image/jpeg', 'image/jpg'])

if __name__ == '__main__':
    unittest.main()
