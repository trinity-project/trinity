"""Author: Trinity Core Team

MIT License

Copyright (c) 2018 Trinity

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

from sserver.model.models import DbManager


class Message(DbManager):
    """

    """
    db_table = DbManager.objects.db.Message
    primary_key = "_id"
    required_item = ["address", "type", "info", "state"]

    def __init__(self, **kwargs):
        self.contents = kwargs
        if self.db_table:
            self.db_table.create_index(self.primary_key)

    @staticmethod
    def put_message(address, type, info, state):
        return Message(address=address, type=type, info=info, state=state).save()

    @staticmethod
    def update_message_state(id, state):
        filter = {"_id": id}
        return Message().update(filter, state=state)

    @staticmethod
    def get_message(address):
        messages = Message().query({"address": "test2"}, query_all=True)
        return [i for i in messages]


if __name__ == "__main__":
    result = Message.put_message(address = "test2", type = "trans", info="{'mytest':'mytest'}", state = "pending")
    message = Message().query({"address": "test2", "state":"pending"}, query_all=True)
    for i in message:
        print(i)
        id = i.get("_id")
        Message.update_message_state(id, "close")
