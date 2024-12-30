import unittest
from unittest.mock import patch, Mock
from megabot.song import Song


class TestSong(unittest.TestCase):
    """Testing Song module"""
    def setUp(self) -> None:
        """given each test new yt_dl mock"""
        self.patcher_ydl = patch('yt_dlp.YoutubeDL')
        self.mock_ydl = self.patcher_ydl.start()
        self.mock_ydl_instance = self.mock_ydl.return_value.__enter__
        self.mock_ydl_instance_ret = self.mock_ydl.return_value.__enter__.return_value
        self.mock_ydl_instance_side = self.mock_ydl.return_value.__enter__.side_effect
        # self.song = song("My Hero")
        return super().setUp()

    def tearDown(self) -> None:
        """destroying that yt_dl mock"""
        self.patcher_ydl.stop()
        return super().tearDown()

    def _test_song_attributes(
            self,
            test_song,
            dummy_info: dict,
            url: str = "https://www.youtube.com/channel/UCGRjJrpD2bmk9Ilq6nq80qg",
            title: str = "42",
            channel: str = "GordonFreeman",
            duration: str = "4:20",
            stream_url: str = "blablatoolongurl",
            channel_url: str = "https://www.youtube.com/channel/UCGRjJrpD2bmk9Ilq6nq80qg",
            thumbnail_url: str = "https://i.ytimg.com/vi_webp/EqWRaAF6_WY/maxresdefault.webp",
            valid: bool = True,
    ) -> None:
        """helper func to check for class attributes"""

        self.assertEqual(test_song.infos, dummy_info)
        self.assertEqual(test_song.url, url)
        self.assertEqual(test_song.title, title)
        self.assertEqual(test_song.channel, channel)
        self.assertEqual(test_song.duration, duration)
        self.assertEqual(test_song.stream_url, stream_url)
        self.assertEqual(test_song.channel_url, channel_url)
        self.assertEqual(test_song.thumbnail_url, thumbnail_url)
        if valid:
            self.assertTrue(test_song.valid)
        else:
            self.assertFalse(test_song.valid)

    def test_get_infos_with_url(self):
        """test func get_infos given an url"""
        url = "https://www.youtube.com/watch?v=EqWRaAF6_WY"
        dummy_info_url = {
            "fulltitle": "42",
            "original_url": url,
            "channel": "GordonFreeman",
            "duration": "4:20",
            "url": "blablatoolongurl",
            "channel_url": "https://www.youtube.com/channel/UCGRjJrpD2bmk9Ilq6nq80qg",
            "thumbnail": "https://i.ytimg.com/vi_webp/EqWRaAF6_WY/maxresdefault.webp"
        }

        self.mock_ydl_instance_ret.extract_info.return_value = Mock()
        self.mock_ydl_instance_ret.sanitize_info.return_value = dummy_info_url

        # reinitialize our Song object with an url
        test_song = Song("https://www.youtu.be/")
        test_song.get_infos(content=url)

        self._test_song_attributes(dummy_info=dummy_info_url, test_song=test_song, url=url)

    def test_get_infos_with_title(self):
        """test func get_infos given a title"""
        title = "My Hero"
        dummy_info_url = {
            "entries": [
                {
                    "fulltitle": title,
                    "original_url": "https://www.youtube.com/channel/UCGRjJrpD2bmk9Ilq6nq80qg",
                    "channel": "GordonFreeman",
                    "duration": "4:20",
                    "url": "blablatoolongurl",
                    "channel_url": "https://www.youtube.com/channel/UCGRjJrpD2bmk9Ilq6nq80qg",
                    "thumbnail": "https://i.ytimg.com/vi_webp/EqWRaAF6_WY/maxresdefault.webp"
                }
            ]
        }

        self.mock_ydl_instance_ret.extract_info.return_value = Mock()
        self.mock_ydl_instance_ret.sanitize_info.return_value = dummy_info_url

        # reinitialize our Song object with an url
        test_song = Song("42")
        test_song.get_infos(content=title)

        self._test_song_attributes(dummy_info=dummy_info_url, test_song=test_song, title=title)

    def test_get_infos_invalid_title(self):
        """test func get_infos given an invalid title, or yt_dl error"""
        title = "Voldemort"
        self.mock_ydl_instance_ret.extract_info.side_effect = Exception

        with self.assertRaises(Exception) as ctx:
            self.assertFalse(Song(title).valid)
        self.assertEqual(str(ctx.exception), f"Couldn't find {title}")

    def test_reload_infos_successful(self):
        """test func reload_infos"""
        test_song = Song("")

        with patch.object(test_song, 'get_infos', return_value=None):
            result = test_song.reload_infos()
        self.assertTrue(result)

    def test_relaod_infos_failure(self):
        """test func reload_infos but get_infos returns an error"""
        url = "https://www.youtube.com/watch?v=EqWRaAF6_WY"

        test_song = Song("")
        test_song.url = url

        with patch.object(test_song, 'get_infos', side_effect=Exception):
            with self.assertRaises(Exception) as ctx:
                test_song.reload_infos()
        self.assertEqual(str(ctx.exception), f"cant reload infos ({test_song.url})")


if __name__ == "__main__":
    unittest.main()
