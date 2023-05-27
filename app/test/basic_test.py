import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

print(sys.path)

from app.app import app, db
import unittest

mysql = {
    'user': 'root',
    'passwd': '',
    'host': 'localhost',
    'db': 'paper_test'
}

username = "haoaho"
password = "123456"

mysqlConfig = "mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4" \
    .format(mysql['user'], mysql['passwd'], mysql['host'], mysql['db'])

class BasicTest(unittest.TestCase):
    def setUp(self):
        with app.app_context():
            app.config["TESTING"] = True
            app.config["DEBUG"] = False
            app.config["SQLALCHEMY_DATABASE_URI"] = mysqlConfig
            self.app = app.test_client()
            db.drop_all()
            db.create_all()
            self.assertEqual(app.debug, False)


if __name__ == "__main__":
    unittest.main()