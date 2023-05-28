import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

print(sys.path)

from app.app import app, db
import unittest

class BasicTest(unittest.TestCase):
    def setUp(self):
        with app.app_context():
            app.config["TESTING"] = True
            app.config["DEBUG"] = False
            self.app = app.test_client()
            db.drop_all()
            db.create_all()
            self.assertEqual(app.debug, False)


if __name__ == "__main__":
    unittest.main()