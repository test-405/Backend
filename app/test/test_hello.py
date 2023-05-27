from .basic_test import BasicTest

class HelloTest(BasicTest):
    def test_hello(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)