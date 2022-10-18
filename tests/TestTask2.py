import unittest
import requests
import tests.BasicTest
import requests
import os


class TestTask2(tests.BasicTest.BasicTest):
    def testCheckWorkingDirectory(self):
        self.assertFalse(os.getcwd().removesuffix(os.sep).endswith(os.sep + 'tests'),
                         "Please set your working directory to the project root (instead of xxx/tests) in `Edit Configurations`.")

    def testIndex(self):
        resp = requests.get(self.server_base + "data/index.html", headers=self.requests_headers)
        self.assertHTTP200(resp)
        flen = self.assertFileContentEqual("data/index.html", resp.content)
        self.assertIn('text/html', resp.headers.get('Content-Type'))
        self.assertEqual(resp.headers.get('Content-Length'), str(flen))

    def test_js(self):
        resp = requests.get(self.server_base + "data/main.js", headers=self.requests_headers)
        self.assertHTTP200(resp)
        flen = self.assertFileContentEqual("data/main.js", resp.content)
        self.assertIn('/javascript', str(resp.headers.get('Content-Type')).lower())
        # may be application/javascript and text/javascript
        self.assertEqual(resp.headers.get('Content-Length'), str(flen))

    def test_sakana(self):
        resp = requests.get(self.server_base + "data/test.jpg", headers=self.requests_headers)
        self.assertHTTP200(resp)
        flen = self.assertFileContentEqual("data/test.jpg", resp.content)
        self.assertIn('image/jpeg', str(resp.headers.get('Content-Type')).lower())
        self.assertEqual(resp.headers.get('Content-Length'), str(flen))


if __name__ == '__main__':
    unittest.main()
