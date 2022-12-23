import unittest
import requests
import threading
import time
import random
import socket
import string
import main


def random_string(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


def generate_junk(length):
    return 'AAAA' * length

class Reply():
    def __init__(self, status_code, reason, headers, body, content, ):
        # print(headers)
        self.status_code = status_code
        self.reason = reason
        self.headers = headers
        self.body = body
        self.content = body
        if 'Set-Cookie' in headers:
            self.cookies = headers['Set-Cookie']
            self.cookies = self.cookies.split(';')[0]
        else:
            self.cookies = None

    def __str__(self):
        return f"Reply({self.status_code}, {self.reason}, {self.headers},{self.cookies} ,{self.body}, {self.content})"

class Request():
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.headers = {
            "User-Agent": 'cs305-client',
            "Accept": "*/*",
        }

    @staticmethod
    def prepare_header(method: str, path: str, host: str, headers: dict = None, cookies: dict = None) -> str:
        retunr_str = method + " " + path + " HTTP/1.1\r\n"
        retunr_str += "Host: " + host + "\r\n"
        if headers is not None:
            for key in headers:
                if headers[key] is not None:
                    retunr_str += key + ": " + headers[key] + "\r\n"
                else:
                    retunr_str += key + ": null\r\n"
        if cookies is not None:
            retunr_str += "Cookie: "
            for key in cookies:
                retunr_str += key + "=" + cookies[key] + "; "
            retunr_str = retunr_str[:-2] + "\r\n"
        retunr_str += "\r\n"
        return retunr_str

    @staticmethod
    def head(url: str, headers: dict = None, cookies: dict = None, timeouts: int = 5, **kwargs) -> Reply:
        sok = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sok.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        headers1 = {
            "User-Agent": 'cs305-client',
            "Accept": "*/*",
        }
        host = url.split('/')[2]
        port = host.split(':')[1] if ':' in host else 80
        path = url.split(host)[1]
        sok.connect((host.split(':')[0] if ':' in host else host, int(port)))
        if headers is not None:
            headers1.update(headers)
        request = Request.prepare_header("HEAD", path, host, headers1, cookies)
        sok.sendall(request.encode())
        data = bytearray()
        sok.settimeout(timeouts)
        while True:
            try:
                data1 = sok.recv(1)
                data += data1
                if not data1:
                    break
            except socket.timeout:
                sok.close()
                print('time out')
                return Reply(0, 'time out', {}, b'', b'')
            except socket.error as e:
                raise e
        sok.close()
        body = data.split(b'\r\n\r\n', maxsplit=1)[1]
        if body == b'':
            pass
        else:
            raise Exception("HEAD body is not empty")
        status_code = int(data.split(b'\r\n')[0].split(b' ')[1])
        reason = data.split(b'\r\n')[0].split(b' ')[2].decode()
        headerlist = data.split(b'\r\n\r\n', maxsplit=1)[0].decode().split('\r\n')
        headers = dict()
        for header in headerlist[1:]:
            split = header.split(':')
            if len(split) > 1:
                headers.update({split[0]: split[1].removeprefix(' ')})
        return Reply(status_code, reason, headers, body, '')

    @staticmethod
    def post(url: str, headers: dict = None, cookies: dict = None, json: dict = None, data: str = None,
             timeouts: int = 5,
             package_length: int = 1024, package_interval: float = 0, **kwargs) -> Reply:
        sok = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sok.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        headers1 = {
            "User-Agent": 'cs305-client',
            "Accept": "*/*",
        }
        host = url.split('/')[2]
        port = host.split(':')[1] if ':' in host else 80
        path = url.split(host)[1]
        sok.connect((host.split(':')[0] if ':' in host else host, int(port)))
        if json is not None:
            headers1["Content-Type"] = "application/json"
            import json as json1
            headers1["Content-Length"] = str(len(json1.dumps(json)))
        if data is not None:
            headers1["Content-Type"] = "application/x-www-form-urlencoded"
            headers1["Content-Length"] = str(len(data))
        if headers is not None:
            headers1.update(headers)
        request = Request.prepare_header("POST", path, host, headers1, cookies)
        if json is not None:
            import json as json1
            request += json1.dumps(json)
        if data is not None:
            request += data
        request = request.encode()
        # split request in package length
        request = [request[i:i + package_length] for i in range(0, len(request), package_length)]
        a = 0
        for i in request:
            sok.sendall(i)
            a = a + 1
            time.sleep(package_interval)
        data = bytearray()
        sok.settimeout(timeouts)
        while True:
            try:
                data1 = sok.recv(1024)
                data += data1
                if not data1:
                    break
            except socket.timeout:
                sok.close()
                print('time out')
                return Reply(0, 'time out', {}, b'', b'')
            except socket.error as e:
                raise e
        sok.close()
        status_code = int(data.split(b'\r\n')[0].split(b' ')[1])
        reason = data.split(b'\r\n')[0].split(b' ')[2].decode()
        headerlist = data.split(b'\r\n\r\n', maxsplit=1)[0].decode().split('\r\n')
        headers = dict()
        for header in headerlist[1:]:
            split = header.split(':')
            if len(split) > 1:
                headers.update({split[0]: split[1].removeprefix(' ')})
        body = data.split(b'\r\n\r\n', maxsplit=1)[1]
        content = body.decode()
        return Reply(status_code, reason, headers, body, content)

    @staticmethod
    def get(url: str, headers: dict = None, cookies: dict = None, timeouts: int = 5, package_length: int = 1024,
            package_interval: float = 0, **kwargs) -> Reply:
        sok = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sok.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        headers1 = {
            "User-Agent": 'cs305-test-bot',
            "Accept": "*/*",
        }
        host = url.split('/')[2]
        port = host.split(':')[1] if ':' in host else 80
        path = url.split(host)[1]
        sok.connect((host.split(':')[0] if ':' in host else host, int(port)))
        if headers is not None:
            headers1.update(headers)
        request = Request.prepare_header("GET", path, host, headers1, cookies)
        request = request.encode()
        # split request in package length
        request = [request[i:i + package_length] for i in range(0, len(request), package_length)]
        a = 0
        for i in request:
            sok.sendall(i)
            a = a + 1
            time.sleep(package_interval)
        data = bytearray()
        sok.settimeout(timeouts)
        while True:
            try:
                data1 = sok.recv(1024)
                data += data1
                if not data1:
                    break
            except socket.timeout:
                sok.close()
                print('time out')
                return Reply(0, 'time out', {}, b'', b'')
            except socket.error as e:
                raise e
        sok.close()
        status_code = int(data.split(b'\r\n')[0].split(b' ')[1])
        reason = data.split(b'\r\n')[0].split(b' ')[2].decode()
        headerlist = data.split(b'\r\n\r\n', maxsplit=1)[0].decode().split('\r\n')
        headers = dict()
        for header in headerlist[1:]:
            split = header.split(':')
            if len(split) > 1:
                headers.update({split[0]: split[1].removeprefix(' ')})
        body = data.split(b'\r\n\r\n', maxsplit=1)[1]
        content = data
        return Reply(status_code, reason, headers, body, content)

class CS305Ass1FinalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = main.http_server
        cls.run_thread = threading.Thread(target=cls.server.run)
        # cls.run_thread.setDaemon(True)
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
        sid = main.YOUR_STUDENT_ID
        print("\n\n")
        print("==========")
        print(f"Test for {sid} Ends.")
        print("==========")

    # general methods
    def assertHTTP200(self, resp):
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.reason, 'OK')

    def assertFileContentEqual(self, filepath, bdata) -> int:
        with open(filepath, "rb") as f:
            fbd = f.read()
            self.assertEqual(bdata, fbd)
            return len(fbd)

    # Task 1
    def testTask1_1_404NotFound(self):
        resp = requests.get(self.server_base, headers=self.requests_headers, timeout=5)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.reason, 'Not Found')
        # You can ignore `Accept-Encoding: identity` when running unittests
        #   , and you don't need to handle it in your code

    def testTask1_2_400BadRequestWithWrongHost(self):
        headers = self.requests_headers.copy()
        headers['Host'] = 'www.sustech.edu.cn'
        resp = requests.get(self.server_base, headers=headers, timeout=5)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.reason, 'Bad Request')

    def testTask1_3_405MethodNotAllowed(self):
        resp = requests.options(self.server_base, headers=self.requests_headers, timeout=5)
        self.assertEqual(resp.status_code, 405)
        self.assertEqual(resp.reason, 'Method Not Allowed')

    def testTaskExt1_4_GetWithInterval(self):
        headers = self.requests_headers.copy()
        headers["X-" + random_string(100)] = random_string(100)
        resp = Request.get(url=self.server_base, headers=headers, package_length=256, package_interval=2)
        self.assertEqual(resp.status_code, 404)

    # Task 2
    def testTask2_1_Index(self):
        resp = requests.get(url = self.server_base + "data/index.html",headers=self.requests_headers, timeout=5)
        self.assertHTTP200(resp)
        flen = self.assertFileContentEqual("data/index.html", resp.content)
        self.assertIn('text/html', resp.headers.get('Content-Type'))
        self.assertEqual(resp.headers.get('Content-Length'), str(flen))

    def testTask2_2_js(self):
        resp = requests.get(self.server_base + "data/main.js", headers=self.requests_headers, timeout=5)
        self.assertHTTP200(resp)
        flen = self.assertFileContentEqual("data/main.js", resp.content)
        self.assertIn('/javascript', str(resp.headers.get('Content-Type')).lower())
        # may be application/javascript and text/javascript
        self.assertEqual(resp.headers.get('Content-Length'), str(flen))
    
    def testTask2_3_sakana(self):
        resp = requests.get(self.server_base + "data/test.jpg", headers=self.requests_headers, timeout=5)
        self.assertHTTP200(resp)
        flen = self.assertFileContentEqual("data/test.jpg", resp.content)
        self.assertIn('image/jpeg', str(resp.headers.get('Content-Type')).lower())
        self.assertEqual(resp.headers.get('Content-Length'), str(flen))

    def testTaskExt2_4_IndexHead(self):
        resp = Request.head(self.server_base + "data/index.html", headers=self.requests_headers)
        self.assertHTTP200(resp)
        # cl = resp.headers.get('Content-Length')
        # with open("data/index.html", "rb") as f:
        #     flen = len(f.read())
        # self.assertTrue(int(cl) == flen)
        self.assertEqual(len(resp.content), 0)

    def testTaskExt2_5_js_head(self):
        resp = Request.head(self.server_base + "data/main.js", headers=self.requests_headers)
        self.assertHTTP200(resp)
        # cl = resp.headers.get('Content-Length')
        # with open("data/main.js", "rb") as f:
        #     flen = len(f.read())
        # self.assertTrue(int(cl) == flen)
        self.assertEqual(len(resp.content), 0)

    def testTaskExt2_6_sakana_head(self):
        resp = Request.head(self.server_base + "data/test.jpg", headers=self.requests_headers)
        self.assertHTTP200(resp)
        # cl = resp.headers.get('Content-Length')
        self.assertIn('image/jpeg', str(resp.headers.get('Content-Type')).lower())
        # with open("data/test.jpg", "rb") as f:
        #     flen = len(f.read())
        # self.assertTrue(int(cl) == flen)
        self.assertEqual(len(resp.content), 0)

    def testTaskExts2_7_BigHeaderWithInterval(self):
        headers = self.requests_headers.copy()
        for i in range(1, 50):
            headers["X-" + random_string(random.randint(50, 200))] = random_string(random.randint(100, 500))
        resp = Request.get(url=self.server_base + "data/test.jpg", headers=headers, package_interval=0.1)
        self.assertEqual(resp.status_code, 200)
    
    # Task 3
    def testTask3_1_Post(self):
        obj = {
            "data": random_string(10)
        }
        resp = requests.post(self.server_base + "post", json=obj, timeout=5)
        self.assertEqual(resp.status_code, 200)
        resp = requests.get(self.server_base + "post", timeout=5)
        resp_json = resp.json()
        self.assertEqual(obj['data'], resp_json['data'])
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(int(resp.headers.get('Content-Length')), len(resp.content))

    def testTaskExt3_2_Head(self):
        obj = {
            "data": random_string(10),
        }
        resp = requests.post(self.server_base + "post", json=obj, timeout=5)
        self.assertEqual(resp.status_code, 200)
        resp = requests.get(self.server_base + "post", timeout=5)
        resp_json = resp.json()
        self.assertEqual(obj['data'], resp_json['data'])
        self.assertEqual(resp.status_code, 200)
        llen = int(resp.headers.get('Content-Length'))
        self.assertEqual(llen, len(resp.content))
        resp = Request.head(self.server_base + "post")
        # self.assertEqual(int(resp.headers.get('Content-Length')), llen)
        self.assertEqual(len(resp.content), 0)
        self.assertEqual(resp.status_code, 200)

    def testTaskExt3_3_BigPostWithInterval(self):
        obj = {
            "junk": generate_junk(40960),
            "data": random_string(1000),
            "junk2": generate_junk(40960)
        }
        resp = Request.post(self.server_base + "post", json=obj, package_length=1023, package_interval=0.01)
        self.assertEqual(resp.status_code, 200)
        resp = requests.get(self.server_base + "post", timeout=5)
        resp_json = resp.json()
        self.assertEqual(obj['data'], resp_json['data'])
        self.assertEqual(resp.status_code, 200)
        llen = int(resp.headers.get('Content-Length'))
        self.assertEqual(llen, len(resp.content))

    def testTaskExt3_4_CRLFinJson(self):
        import json
        json1 = '''
        {"data": "''' + random_string(1000) + '''",\r\n\r\n\r\n"password": "admin",\r\n\r\n\r\n\r\n"username": "ba enejvn etneagerd"}
        '''
        obj = json.loads(json1)
        resp = Request.post(self.server_base + "post", data=json1, package_length=1023, package_interval=0.01)
        self.assertEqual(resp.status_code, 200)
        resp = requests.get(self.server_base + "post", timeout=5)
        resp_json = resp.json()
        self.assertEqual(obj['data'], resp_json['data'])
        self.assertEqual(resp.status_code, 200)
        llen = int(resp.headers.get('Content-Length'))
        self.assertEqual(llen, len(resp.content))
    
    # Task 4
    def testTask4_1_Redirect(self):
        r = requests.get(self.server_base + "redirect", allow_redirects=False, timeout=5)
        self.assertIn(r.status_code, range(300, 320))
        self.assertEqual(r.reason, 'Found')
        self.assertIn('data/index.html', r.headers.get('Location'))

    def testTaskExt4_2_RedirectHEAD(self):
        r = Request.head(self.server_base + "redirect")
        self.assertIn(r.status_code, range(300, 320))
        self.assertEqual(r.reason, 'Found')
        self.assertEqual(b'', r.body)
        self.assertIn('data/index.html', r.headers.get('Location'))
    
    # Task 5 - Cookie
    def testTask5_1_TestLogin(self):
        resp = requests.post(self.server_base + "api/login", json={"username": "admin", "password": "admin"}, timeout=5)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.cookies.get("Authenticated"), "yes")

    def testTask5_2_TestGetImage(self):
        s = requests.session()
        resp = s.get(self.server_base + "api/getimage", timeout=5)
        self.assertEqual(resp.status_code, 403)

        resp = s.post(self.server_base + "api/login", json={"username": "admin", "password": "admin"}, timeout=5)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.cookies.get("Authenticated"), "yes")

        resp = s.get(self.server_base + "api/getimage", timeout=5)
        self.assertEqual(resp.status_code, 200)
        flen = self.assertFileContentEqual('data/test.jpg', resp.content)
        self.assertEqual(int(resp.headers['Content-Length']), flen)
        self.assertIn(resp.headers['Content-Type'], ['image/jpeg', 'image/jpg'])

    def testTaskExt5_3_TestHEADGetImage(self):
        s = requests.session()
        resp = s.head(self.server_base + "api/getimage", timeout=5)
        self.assertEqual(resp.status_code, 403)

        resp = s.post(self.server_base + "api/login", json={"username": "admin", "password": "admin"}, timeout=5)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.cookies.get("Authenticated"), "yes")

        resp = s.get(self.server_base + "api/getimage", timeout=5)
        self.assertEqual(resp.status_code, 200)
        flen = self.assertFileContentEqual('data/test.jpg', resp.content)
        self.assertEqual(int(resp.headers['Content-Length']), flen)
        self.assertIn(resp.headers['Content-Type'], ['image/jpeg', 'image/jpg'])

        resp = Request.head(self.server_base + "api/getimage", cookies=s.cookies.get_dict())
        self.assertEqual(resp.status_code, 200)
        # self.assertEqual(int(resp.headers['Content-Length']), flen)
        self.assertIn(resp.headers['Content-Type'], ['image/jpeg', 'image/jpg'])
        self.assertEqual(resp.content, b'')

    def testTaskExt5_4_DirectAccess(self):
        cookie = {
            "Authenticated": 'yes',
        }
        for i in range(10):
            cookie[random_string(random.randint(10, 20))] = random_string(random.randint(20, 40))
        resp = Request.get(url=self.server_base + "api/getimage", cookies=cookie)
        self.assertEqual(resp.status_code, 200)
        flen = self.assertFileContentEqual('data/test.jpg', resp.content)
        self.assertEqual(int(resp.headers['Content-Length']), flen)
        self.assertIn(resp.headers['Content-Type'], ['image/jpeg', 'image/jpg'])

    # Task 6 - Session
    def testTask6_1_TestLogin(self):
        resp = requests.post(self.server_base + "apiv2/login", json={"username": "admin", "password": "admin"}, timeout=5)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.cookies.get("SESSION_KEY"))

    def testTask6_2_TestGetImage(self):
        s = requests.session()
        resp = s.get(self.server_base + "apiv2/getimage", timeout=5)
        self.assertEqual(resp.status_code, 403)

        resp = s.post(self.server_base + "apiv2/login", json={"username": "admin", "password": "admin"}, timeout=5)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.cookies.get("SESSION_KEY"))

        resp = s.get(self.server_base + "apiv2/getimage", timeout=5)
        self.assertEqual(resp.status_code, 200)
        flen = self.assertFileContentEqual('data/test.jpg', resp.content)
        self.assertEqual(int(resp.headers['Content-Length']), flen)
        self.assertIn(resp.headers['Content-Type'], ['image/jpeg', 'image/jpg'])

    def testTaskExt6_3_TestHEAD(self):
        s = requests.session()
        resp = s.head(self.server_base + "apiv2/getimage", timeout=5)
        self.assertEqual(resp.status_code, 403)

        resp = s.post(self.server_base + "apiv2/login", json={"username": "admin", "password": "admin"}, timeout=5)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.cookies.get("SESSION_KEY"))

        resp = s.get(self.server_base + "apiv2/getimage", timeout=5)
        self.assertEqual(resp.status_code, 200)
        flen = self.assertFileContentEqual('data/test.jpg', resp.content)
        self.assertEqual(int(resp.headers['Content-Length']), flen)
        self.assertIn(resp.headers['Content-Type'], ['image/jpeg', 'image/jpg'])

        resp = Request.head(url=self.server_base + "apiv2/getimage", cookies=s.cookies.get_dict())
        print(resp)
        self.assertEqual(resp.status_code, 200)
        # self.assertEqual(int(resp.headers['Content-Length']), flen)
        self.assertIn(resp.headers['Content-Type'], ['image/jpeg', 'image/jpg'])
        self.assertEqual(resp.content, b'')

    def testTaskExt6_4_TestMutipleCookie(self):
        s = requests.session()
        resp = s.head(self.server_base + "apiv2/getimage", timeout=5)
        self.assertEqual(resp.status_code, 403)

        resp = s.post(self.server_base + "apiv2/login", json={"username": "admin", "password": "admin"}, timeout=5)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.cookies.get("SESSION_KEY"))

        cookie = s.cookies.get_dict()
        for i in range(10):
            cookie[random_string(random.randint(10, 20))] = random_string(random.randint(20, 40))
        resp = Request.get(url=self.server_base + "apiv2/getimage", cookies=cookie)
        self.assertEqual(resp.status_code, 200)
        flen = self.assertFileContentEqual('data/test.jpg', resp.content)
        self.assertEqual(int(resp.headers['Content-Length']), flen)
        self.assertIn(resp.headers['Content-Type'], ['image/jpeg', 'image/jpg'])

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(CS305Ass1FinalTest)
    tests = list()
    sid = main.YOUR_STUDENT_ID
    for test in suite._tests:
        print(test._testMethodName)
        tests.append(test._testMethodName)
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
    with open("result.csv", "w") as f:
        f.write("SID,")
        for testName in tests:
            f.write(testName + ",")
        f.write("\n")
        f.write(str(sid) + ",")
        results = dict()
        for name in tests:
            results[name] = 1
        for fail in testResult.failures:
            results[fail[0]._testMethodName] = 0
        for fail in testResult.errors:
            results[fail[0]._testMethodName] = 0
        for testName in tests:
            f.write(str(results[testName]) + ",")
    print("Write test result to result.csv")
    # Additional for argue
    print()
    print(f"SID: {sid}")
    print()
    print("File SHA256: ")
    import hashlib
    with open("main.py","rb") as f:
        print(f"main.py:\t{hashlib.md5(f.read()).hexdigest()}")
    with open("framework.py","rb") as f:
        print(f"framework.py:\t{hashlib.md5(f.read()).hexdigest()}")
    with open(__file__,"rb") as f:
        print(f"FinalTest.py:\t{hashlib.md5(f.read()).hexdigest()}")
    print()
    cnt = 0
    passed = 0
    for test in tests:
        if "TaskExt" not in test:
            cnt += 1
            if results[test] == 1:
                passed += 1
    print(f"Passed Basic Tests: {passed}/{cnt}")
    for test in results:
        if "TaskExt" not in test and results[test] == 1:
            print(test)
    if passed != cnt:
        print(f"Failed Basic Tests: {passed}/{cnt}")
        for test in results:
            if "TaskExt" not in test and results[test] == 0:
                print(test)
    import sys
    sys.stdout.flush()
    sys.stderr.flush()
    import os
    os._exit(0)
