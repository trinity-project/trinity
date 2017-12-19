from tnc.channel_manager.channel import Channel
import unittest


class TestChannel(unittest.TestCase):
    def setUp(self):
        self.sender = "0x123456789"
        self.receiver = "0x34567890"
        self.deposit = 100
        self.open_block_number = 100
        self.channel = Channel(self.sender, self.receiver, self.deposit, self.open_block_number)

    def test_to_dict(self):
        channel_dict = self.channel.to_dict()
        self.assertEqual(self.receiver, channel_dict["receiver"])
        self.assertEqual(self.sender, channel_dict["sender"])
        self.assertEqual(self.deposit, channel_dict["deposit"])
        self.assertEqual(self.open_block_number, channel_dict["open_block_number"])


if __name__ == "__main__":
    unittest.main()
