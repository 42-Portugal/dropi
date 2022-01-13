import dropi
import unittest
import pprint as pp
import time

class TestAPI(unittest.TestCase):

    def setUp(self):
        t = dropi.ApiToken()
        self.api = dropi.Api42(t)
        time.sleep(1)


    # request is successful if an exception is not thrown

    # test ensures it is able to do a GET request of Community Service
    def test_API_connection_is_successful(self):
        response = self.api.get("cursus")

    # ensures the GET request works when given a user ID
    def test_GET_of_cursus_user_given_id(self):
        response = self.api.get("users/jodoe/cursus_users")

    # ensures a POST request for a community service
    def test_POST_of_a_community_service(self):
        params = {
            "close": {
                "user_id": "85628",
                "closer_id": "90234",
                "kind": "other",
                "reason": "you are a very naughty bot! 💢",
                "community_services_attributes": [{
                    "duration": 7200,
                }]
            }
        }

    # drop created event 8703 as a test; 
    def test_POST_of_a_feedback_to_an_event(self):

        previous_events = self.api.get("events/8703/feedbacks")
        pp.pprint(previous_events)

        self.api.post("events/8703/feedbacks", data={"feedback": {"comment": "thank you, Drop! This was an amazing event! 🥳"}})


    def test_PATCH_of_a_feedback_to_an_event(self):
        comment = "this is a patched comment! So much fun! 🕺"

        feedbacks = self.api.get("events/8703/feedbacks")
        try:
            feedback = feedbacks[0]['id']
        except IndexError:
            self.api.post("events/8703/feedbacks", data={"feedback": {"comment": "thank you, Drop! This was an amazing event! 🥳"}})
            feedbacks = self.api.get("events/8703/feedbacks")
            feedback = feedbacks[0]['id']
        self.api.patch(f"events/8703/feedbacks/{feedback}", data={"feedback": {"comment": comment}})

        feedbacks = self.api.get(f"feedbacks/{feedback}")

        self.assertEqual(feedbacks["comment"], comment)

    def test_PUT_of_a_feedback_to_an_event(self):
        comment = "this is a patched comment through put! So much fun! 🕺"

        feedbacks = self.api.get("events/8703/feedbacks")
        try:
            feedback = feedbacks[0]['id']
        except IndexError:
            self.api.post("events/8703/feedbacks", data={"feedback": {"comment": "thank you, Drop! This was an amazing event! 🥳"}})
            feedbacks = self.api.get("events/8703/feedbacks")
            feedback = feedbacks[0]['id']
        self.api.put(f"events/8703/feedbacks/{feedback}", data={"feedback": {"comment": comment}})

        feedbacks = self.api.get(f"feedbacks/{feedback}")

        self.assertEqual(feedbacks["comment"], comment)

    def test_DELETE_of_a_feedback_to_an_event(self):
        feedbacks = self.api.get("events/8703/feedbacks")
        try:
            feedback = feedbacks[0]['id']
        except IndexError:
            self.api.post("events/8703/feedbacks", data={"feedback": {"comment": "thank you, Drop! This was an amazing event! 🥳"}})
            feedbacks = self.api.get("events/8703/feedbacks")
            feedback = feedbacks[0]['id']
        prev_count = len(feedbacks)
        response = self.api.delete(f"events/8703/feedbacks/{feedback}", data={"id": feedback})
        time.sleep(0.5)
        feedbacks = self.api.get("events/8703/feedbacks")
        after_count = len(feedbacks)
        self.assertTrue(prev_count - 1 == after_count)
        

if __name__ == '__main__':
    unittest.main()
