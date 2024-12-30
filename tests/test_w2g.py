import unittest
from unittest.mock import patch, Mock
from megabot.w2g import w2g


class Testw2g(unittest.TestCase):
    """Testing w2g module"""
    def setUp(self) -> None:
        dummyAPI = "123456"
        self.room = w2g(dummyAPI)
        return super().setUp()

    @patch('requests.post')
    def test_create_room_post_success(self, mock_req):
        """Testing create_room function"""
        self.assertEqual(self.room.api_key, "123456")

        mock_req.return_value = Mock()
        mock_req.return_value.json.return_value = {
            'streamkey': '42'
        }

        self.assertEqual(self.room.create_room(
            url="https://youtu.be/j3OqAN4ISOw?si=HsLSFnv5yFeXLjJa"),
            ("https://w2g.tv/rooms/42", "42")
        )
        self.assertEqual(self.room.stream_key, "42")
        self.assertEqual(self.room.room_link, "https://w2g.tv/rooms/42")

    @patch('requests.post')
    def test_create_room_post_failure(self, mock_req):
        mock_req.side_effect = ConnectionError

        with self.assertRaises(Exception) as ctx:
            self.room.create_room("https://youtu.be/j3OqAN4ISOw?si=HsLSFnv5yFeXLjJa")
        self.assertEqual(str(ctx.exception), "failed post request")

    @patch('requests.post')
    def test_create_room_room_treats(self, mock_req):
        mock_req.return_value = Mock()
        mock_req.return_value.json.return_value = {
            'streamkey': '42'
        }

        self.assertEqual(self.room.create_room(
            url="https://youtu.be/j3OqAN4ISOw?si=HsLSFnv5yFeXLjJa", bg_color="#1f1f1f", bg_opacity="40"),
            ("https://w2g.tv/rooms/42", "42")
        )

        self.assertEqual(self.room.bg_color, "#1f1f1f")
        self.assertEqual(self.room.bg_opacity, "40")

    @patch('requests.post')
    def test_update_room_post_successful(self, mock_req):
        """Testing update_room function"""
        self.assertEqual(self.room.api_key, "123456")

        mock_req.return_value.ok = True
        self.assertTrue(self.room.update_room(url="https://youtu.be/j3OqAN4ISOw?si=HsLSFnv5yFeXLjJa"))

    @patch('requests.post')
    def test_update_room_post_failure(self, mock_req):
        mock_req.side_effect = ConnectionError
        mock_req.return_value.status_code = 403

        with self.assertRaises(Exception) as ctx:
            self.room.update_room("https://youtu.be/j3OqAN4ISOw?si=HsLSFnv5yFeXLjJa")
        self.assertEqual(str(ctx.exception), "failed post request")


if __name__ == "__main__":
    unittest.main()
