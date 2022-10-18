import unittest
from typing import Iterable

import tests.BasicTest
import tests.TestTask1
import tests.TestTask2
import tests.TestTask3
import tests.TestTask4
import tests.TestTask5Cookie
import tests.TestTask5Session

import main
import sys

classes = [
    tests.TestTask1.TestTask1,
    tests.TestTask2.TestTask2,
    tests.TestTask3.TestTask3,
    tests.TestTask4.TestTask4,
    tests.TestTask5Cookie.TestTask5Cookie,
    tests.TestTask5Session.TestTask5Session,
]

if __name__ == '__main__':
    sid = main.YOUR_STUDENT_ID
    print(f"SID: {sid}", file=sys.stderr)
    runner = unittest.TextTestRunner()
    suite = unittest.TestSuite()
    for _class in classes:
        _object = _class()
        for function_name in dir(_object):
            if function_name.lower().startswith("test"):
                suite.addTest(_class(function_name))
    runner.run(suite)
