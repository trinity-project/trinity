import unittest
import time
from tnc.channel_manager.state import ChannelState,ChannelFile
from tnc.channel_manager.channel import State


class TestChannelState(unittest.TestCase):
    def setUp(self):
        self.receiver = "0x2345678900"
        self.sender = "0x12345678899"
        self.channel_name = "hash59949494"
        self.state = State.OPEN
        self.deposit = 100
        self.open_block_number = 20
        self.channel_state = ChannelState(self.sender)
        self.channel_state.add_channle_to_database(receiver=self.receiver, channel_name=self.channel_name,
                                       state=self.state, deposit=self.deposit, open_block_number=self.open_block_number)
        self.channel_state.find_sender()

    def test_add_channel(self):
        sender = self.channel_state.find_sender()
        self.assertTrue(sender)

    def test_receiver(self):
        self.assertEqual( self.channel_state.receiver_in_database, self.receiver)

    def test_state(self):
        self.assertEqual(self.state.value, self.channel_state.state_in_database)

    def test_channel_name(self):
        self.assertEqual(self.channel_state.channel_name_in_database, self.channel_name)

    def test_update_channel(self):
        update_receiver = "0x2929292929"
        update_channel_name = "hash828288282"
        update_state = State.CLOSED
        update_deposit = 50
        update_open_block = 2
        self.channel_state.update_channel_to_database(receiver=update_receiver, channel_name=update_channel_name, state=update_state,
                                          deposit=update_deposit, open_block_number=update_open_block)
        sender = self.channel_state.find_sender()
        self.assertTrue(sender)
        self.assertEqual(self.channel_state.receiver_in_database, update_receiver)
        self.assertEqual(self.channel_state.state_in_database, update_state.value)
        self.assertEqual(self.channel_state.channel_name_in_database, update_channel_name)

    def tearDown(self):
        self.channel_state.delete_channle_in_database()
        sender = self.channel_state.find_sender()
        self.assertFalse(sender)


class TestChannelFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receiver = "0x1234567890"
        cls.sender = "0x234567890"
        cls.channel_file = ChannelFile(cls.sender, cls.receiver)
        cls.ctime = time.time()

    def setUp(self):
        self.deposit = 1
        self.open_block_number = 20
        self.balance =  12
        self.closed = True
        self.last_signature = None
        self.settle_timeout = -1
        self.confirmed = True
        self.nonce = 0
        self.channel = {"receiver": self.receiver,
                        "sender": self.sender,
                        "deposit": self.deposit,
                        "open_block_number": self.open_block_number,
                        "balance": self.balance,
                        "closed": self.closed,
                        "last_signature": self.last_signature,
                        "settle_timeout": self.settle_timeout,
                        "create_time": self.ctime,
                        "confirmed": self.confirmed,
                        "nonce": self.nonce
                        }

    def test_create_channel(self):
        self.channel_file.create_channel(**self.channel)
        channel_info  = self.channel_file.read_channel()
        self.assertEqual(channel_info, [self.channel])

    def test_update_channel(self):
        channel={ "receiver": self.receiver,
                       "sender": self.sender,
                       "deposit": self.deposit,
                       "open_block_number": self.open_block_number,
                       "balance": 18,
                       "closed": self.closed,
                       "last_signature": self.last_signature,
                       "settle_timeout": self.settle_timeout,
                       "create_time": self.ctime,
                       "confirmed": self.confirmed,
                       "nonce": 123456789
                       }
        self.channel_file.update_channel(**channel)
        channel_info = self.channel_file.read_channel()
        self.assertEqual(channel_info[0], self.channel)
        channel_info = self.channel_file.read_channel()
        self.assertEqual(channel_info[1], channel)
        
    @classmethod
    def tearDownClass(cls):
        cls.channel_file.delete_channel()


if __name__ == "__main__":
    unittest.main()
