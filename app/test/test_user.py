from .basic_test import BasicTest, username, password

data = {
    "username": username,
    "password": password
}

class UserUtil(BasicTest):
    def register(self):
        headers = {
            "Content-Type": "application/json"
        } 

        response = self.app.post("/api/user/register", headers=headers, json=data)
        return response

    def login(self):
        self.register()
        headers = {
            "Content-Type": "application/json"
        }

        response = self.app.post("/api/user/login", headers=headers, json=data)
        return response
    
    def logout(self):
        access_token = self.login().json["data"]["access_token"]

        headers = {
            "Content-Type": "application/json"
        }

        headers["Authorization"] = f'Bearer {access_token}'
        response = self.app.post("/api/user/logout", headers=headers)
        return response
    
    def build_jwt_head(self):
        access_token = self.login().json["data"]["access_token"]

        headers = {
            "Authorization": f'Bearer {access_token}'
        }

        self.headers = headers

class TestUser(UserUtil):
    def test_register(self):
        response = self.register()
        self.assertEqual(response.status_code, 201)

    def test_login(self):
        response = self.login()
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        response = self.logout()
        self.assertEqual(response.status_code, 200)