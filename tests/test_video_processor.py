import unittest
from app.services.video_processor import VideoProcessor

class TestVideoProcessor(unittest.TestCase):
    def test_queue(self):
        processor = VideoProcessor('rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov')
        self.assertFalse(processor.queue.full())
        processor.stop()

if __name__ == '__main__':
    unittest.main()