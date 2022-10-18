import random
import string
import unittest
import requests
import tests.BasicTest
import requests
import os


class TestTask4(tests.BasicTest.BasicTest):
    def testRedirect(self):
        r = requests.get(self.server_base + "redirect", allow_redirects=False)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.reason, 'Found')
        self.assertEqual(r.headers.get('Location'), "http://127.0.0.1:8080/data/index.html")


if __name__ == '__main__':
    unittest.main()
