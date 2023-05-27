import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

print(sys.path)

import unittest

DB_USER = os.getenv("DB_USER", default="root")
DB_PASSWORD = os.getenv("DB_PASSWORD", default="")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", default="paper_test")
mysql = {
    'user': DB_USER,
    'passwd': DB_PASSWORD,
    'host': 'localhost',
    'db': MYSQL_DATABASE
}
print(sys.path)
print(mysql)

username = "haoaho"
password = "123456"

mysqlConfig = "mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4" \
    .format(mysql['user'], mysql['passwd'], mysql['host'], mysql['db'])

class BasicTest(unittest.TestCase):
    def setUp(self):
        from app.app import app
        with app.app_context():
            app.config["TESTING"] = True
            app.config["DEBUG"] = False
            app.config["SQLALCHEMY_DATABASE_URI"] = mysqlConfig
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