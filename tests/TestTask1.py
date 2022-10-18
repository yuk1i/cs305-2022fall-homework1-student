import unittest
import requests
import tests.BasicTest
import requests


class TestTask1(tests.BasicTest.BasicTest):
    def test404NotFound(self):
        resp = requests.get(self.server_base, headers=self.requests_headers)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.reason, 'Not Found')
        # You can ignore `Accept-Encoding: identity` when running unittests
        #   , and you don't need to handle it in your code

    def test400BadRequestWithWrongHost(self):
        headers = self.requests_headers.copy()
        headers['Host'] = 'www.sustech.edu.cn'
        resp = requests.get(self.server_base, headers=headers)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.reason, 'Bad Request')

    def test405MethodNotAllowed(self):
        resp = requests.options(self.server_base, headers=self.requests_headers)
        self.assertEqual(resp.status_code, 405)
        self.assertEqual(resp.reason, 'Method Not Allowed')


if __name__ == '__main__':
    unittest.main()
