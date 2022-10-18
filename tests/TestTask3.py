import random
import string
import unittest
import requests
import tests.BasicTest
import requests
import os


def random_string(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


def generate_junk(length):
    return 'AAAA' * length


class TestTask3(tests.BasicTest.BasicTest):
    def testPost(self):
        obj = {
            "data": random_string(10)
        }
        resp = requests.post(self.server_base + "post", json=obj)
        self.assertEqual(resp.status_code, 200)
        resp = requests.get(self.server_base + "post")
        resp_json = resp.json()
        self.assertEqual(obj['data'], resp_json['data'])
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(int(resp.headers.get('Content-Length')), len(resp.content))


if __name__ == '__main__':
    unittest.main()
