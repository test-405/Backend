from .basic_test import BasicTest, BasicUtil

class HelloTest(BasicTest):
    def setUp(self):
        self.hello_util = BasicUtil()
    
    def test_hello(self):
        response = self.hello_util.app.get("/")
        self.assertEqual(response.status_code, 200)