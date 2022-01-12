import dropi
import unittest
import pprint as pp

class TestAPI(unittest.TestCase):

    def setUp(self):
        t = dropi.ApiToken()
        self.api = dropi.Api42(t)

    # request is successful if an exception is not thrown

    # test ensures it is able to do a GET request of Community Service
    def test_API_connection_is_successful(self):
        response = self.api.get("cursus")

    # ensures the GET request works when given a user ID
    def test_GET_of_cursus_user_given_id(self):
        response = self.api.get("users/jodoe/cursus_users")

    def test_POST_of_cursus_user_given_id(self):

        old_points_count = int(self.api.get("users/jodoe")['correction_point'])
        response = self.api.post("users/jodoe/correction_points/add")
        new_points_count = int(self.api.get("users/jodoe")['correction_point'])

        self.AssertEqual(old_points_count + 1, new_points_count)
        

if __name__ == '__main__':
    unittest.main()
