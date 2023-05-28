from .basic_test import BasicTest, BasicUtil

class UserUtil(BasicUtil):
    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password

    def register(self):
        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "username": self.username,
            "password": self.password
        }

        response = self.app.post("/api/user/register", headers=headers, json=data)
        return response

    def login(self):
        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "username": self.username,
            "password": self.password
        }

        response = self.app.post("/api/user/login", headers=headers, json=data)
        self.access_token = response.json["data"]["access_token"]
        return response
    
    def logout(self):
        if not hasattr(self, "access_token"):
            raise Exception("You must login first")

        headers = {
            "Content-Type": "application/json"
        }

        headers["Authorization"] = f'Bearer {self.access_token}'
        response = self.app.post("/api/user/logout", headers=headers)
        return response
    
    # equal to register and login
    def build_jwt_head(self):
        self.register()
        access_token = self.login().json["data"]["access_token"]

        headers = {
            "Authorization": f'Bearer {access_token}'
        }

        self.headers = headers
        self.access_token = access_token

class TestUser(BasicTest):
    def setUp(self):
        super().setUp()
        self.user_util = UserUtil("test", "test")

    def test_register(self):
        response = self.user_util.register()
        self.assertEqual(response.status_code, 201)

    def test_login(self):
        response = self.user_util.register()
        response = self.user_util.login()
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        response = self.user_util.register()
        response = self.user_util.login()
        response = self.user_util.logout()
        self.assertEqual(response.status_code, 200)