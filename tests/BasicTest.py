import threading
import unittest

try:
    import main
except ModuleNotFoundError:
    from .. import main


class BasicTest(unittest.TestCase):
    suiteTest = False
    run_thread = None
    server = None

    @classmethod
    def setUpClass(cls):
        cls.server = main.http_server
        cls.run_thread = threading.Thread(target=cls.server.run)
        cls.run_thread.setDaemon(True)
        cls.run_thread.start()
        cls.server_base = f'http://{cls.server.host}/'
        cls.requests_headers = {
            "Connection": "close",
            "Accept-Encoding": None
        }
        import os
        if os.getcwd().removesuffix(os.sep).endswith(os.sep + 'tests'):
            print(os.getcwd())
            print("chdir to ..")
            os.chdir('..' + os.sep)
            print(os.getcwd())

    @classmethod
    def tearDownClass(cls):
        if cls.suiteTest:
            cls.server.listen_socket.close()

    def assertHTTP200(self, resp):
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.reason, 'OK')

    def assertFileContentEqual(self, filepath, bdata) -> int:
        with open(filepath, "rb") as f:
            fbd = f.read()
            self.assertEqual(bdata, fbd)
            return len(fbd)

    def runTest(self):
        self.run()


if __name__ == '__main__':
    unittest.main()
