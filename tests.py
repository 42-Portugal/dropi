import dropi
import unittest

class TestAPI(unittest.TestCase):

    def setUp(self):
        t = dropi.ApiToken()
        api = dropi.Api42(t)

    # test ensures it is able to do a GET request
    def test_API_connection_is_successful(self):
        pass

if __name__ == '__main__':
    unittest.main()
