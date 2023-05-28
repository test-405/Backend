import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

print(sys.path)

import unittest

class BasicTest(unittest.TestCase):
    def setUp(self):
        from app.app import app
        with app.app_context():
            app.config["TESTING"] = True
            app.config["DEBUG"] = False
            self.app = app.test_client()
            from app.app import db
            print("+++++++++")
            print(mysqlConfig)
            print("+++++++++")
            db.drop_all()
            db.create_all()
            self.assertEqual(app.debug, False)


if __name__ == "__main__":
    unittest.main()