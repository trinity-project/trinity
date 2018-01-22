def split_channel_name(channel_name):
    sender_addr = channel_name[::2]
    receiver_addr = channel_name[1::2]
    return sender_addr, receiver_addr
