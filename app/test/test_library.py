from .basic_test import BasicTest
from .test_user import UserUtil

class LibraryUtil(UserUtil):
    def __init__(self, username, password):
        super().__init__(username, password)

    def create_library(self, topic="", desc="", is_public=True):
        self.headers['Content-Type'] = 'application/json'
        
        data = {
            "topic": topic,
            "desc": desc,
            "is_public": is_public
        }

        response = self.app.post("/api/library", headers=self.headers, json=data)
        return response
    
    def create_multiple_library(self, num):
        is_public = False
        for i in range(num):
            self.create_library(f"topic{i}", f"desc{i}", is_public)
            is_public = not is_public
    
    def get_library(self, page_num=1, page_size=5):
        params = {
            "page_num": page_num,
            "page_size": page_size,
            "topic": "topic",
        }
        response = self.app.get(f"/api/library", query_string=params)
        return response
    
    def modify_library(self, library_id, topic="", desc="", is_public=True):
        self.headers['Content-Type'] = 'application/json'
        
        data = {
            "topic": topic,
            "desc": desc,
            "is_public": is_public
        }

        response = self.app.put(f"/api/library/{library_id}", headers=self.headers, json=data)
        return response

    def delete_library(self, library_id):
        response = self.app.delete(f"/api/library/{library_id}", headers=self.headers)
        return response

class TestLibrary(BasicTest):
    def setUp(self):
        super().setUp()
        self.library_util = LibraryUtil("test", "test")
        self.library_util.build_jwt_head()

    def test_create_library(self):
        response = self.library_util.create_library()
        self.assertEqual(response.status_code, 200)

    def test_get_library(self):
        self.library_util.create_multiple_library(10)
        response = self.library_util.get_library()
        self.assertEqual(response.status_code, 200)
    
    def test_modify_library(self):
        response = self.library_util.create_library()
        library_id = response.json["data"]["library_id"]
        response = self.library_util.modify_library(library_id, topic="hhh")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["data"]["topic"], "hhh")

    def test_delete_library(self):
        response = self.library_util.create_library()
        library_id = response.json["data"]["library_id"]
        response = self.library_util.delete_library(library_id)
        self.assertEqual(response.status_code, 200)
    