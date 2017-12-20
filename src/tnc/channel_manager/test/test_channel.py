from tnc.channel_manager.channel import Channel
from tnc.channel_manager.test import test_state
import unittest
import time

class TestChannel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sender = "0x123456789"
        cls.receiver = "0x34567890"
        cls.deposit = 100
        cls.open_block_number = 100
        cls.channel = Channel(cls.sender, cls.receiver, cls.deposit, cls.open_block_number)

    def test01_to_dict(self):
        channel_dict = self.channel.to_dict
        self.assertEqual(self.receiver, channel_dict["receiver"])
        self.assertEqual(self.sender, channel_dict["sender"])
        self.assertEqual(self.deposit, channel_dict["deposit"])
        self.assertEqual(self.open_block_number, channel_dict["open_block_number"])

    def test02_create(self):
        self.channel.create()
        self.assertTrue(self.channel.find_sender())
        self.assertTrue(self.channel.check_channelfile())
        channel = self.channel.read_channel()

    def test03_sender_to_receiver(self):
        self.channel.sender_to_receiver(5)
        channel_info = self.channel.read_channel()
        channel = Channel.from_dict(channel_info[-1])
        self.assertEqual(channel.balance, self.deposit-5)
        self.channel.sender_to_receiver(5)
        channel_info = self.channel.read_channel()
        channel = Channel.from_dict(channel_info[-1])
        self.assertEqual(channel.balance, self.deposit-10)

    def test04_close(self):
        self.channel.close()
        self.assertTrue(self.channel.check_closed())

    @classmethod
    def tearDownClass(cls):
        cls.channel.close()
        cls.channel.delete()


if __name__ == "__main__":
    unittest.main()
