import unittest
from unittest.mock import patch, Mock
from src.megabot.w2g import w2g


class Testw2g(unittest.TestCase):
    def setUp(self) -> None:
        dummyAPI = "123456"
        self.room = w2g(dummyAPI)
        return super().setUp()

    @patch('requests.post')
    def test_create_room(self, mock_req):
        self.assertEqual(self.room.api_key, "123456")

        with self.subTest("valid post request"):
            mock_req.return_value = Mock()
            mock_req.return_value.json.return_value = {
                'streamkey': '42'
            }

            self.assertEqual(self.room.create_room(url="https://youtu.be/j3OqAN4ISOw?si=HsLSFnv5yFeXLjJa"), ("https://w2g.tv/rooms/42", "42"))
            self.assertEqual(self.room.stream_key, "42")
            self.assertEqual(self.room.room_link, "https://w2g.tv/rooms/42")

        with self.subTest("failed post request"):
            mock_req.side_effect = ConnectionError

            with self.assertRaises(Exception) as ctx:
                self.room.create_room("https://youtu.be/j3OqAN4ISOw?si=HsLSFnv5yFeXLjJa")
            self.assertEqual(str(ctx.exception), "failed post request")

    @patch('requests.post')
    def test_update_room(self, mock_req):
        self.assertEqual(self.room.api_key, "123456")

        with self.subTest("valid post request"):
            mock_req.return_value.ok = True
            self.assertTrue(self.room.update_room(url="https://youtu.be/j3OqAN4ISOw?si=HsLSFnv5yFeXLjJa"))

        with self.subTest("failed post request"):
            mock_req.side_effect = ConnectionError

            with self.assertRaises(Exception) as ctx:
                self.room.update_room("https://youtu.be/j3OqAN4ISOw?si=HsLSFnv5yFeXLjJa")
            self.assertEqual(str(ctx.exception), "failed post request")


if __name__ == "__main__":
    unittest.main()
