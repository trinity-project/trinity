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

from sserver.models import Address
import re
import functools
from exception import AddressError


AddressType = {"NEO": r"^A\S+",
               "ETH":r"",
               "BTC": r""}


def check_address_format(func):
    """
    check the address format, should the address as the first option and tye as the second one.
    eg
    @check_address_format
    def add_address(address, address_type, public_key):
        pass
    :param func:
    :return:
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if len(args) > 1:
            address = args[0]
            address_type = args[1]
        elif len(args) == 1:
            address = args[0]
            try:
                address_type = kwargs["address_type"]
            except:
                raise
        else:
            try:
                address = kwargs["address"]
                address_type = kwargs["address_type"]
            except:
                raise
        if re.match(AddressType.get(address_type.upper()),address):
            return func(*args, **kwargs)
        else:
            raise AddressError("Address Format Error")
    return wrapper


@check_address_format
def add_address(address, address_type, public_key, ip_address=None):
    if query_address(address):
        raise AddressError("Address %s already in the database" %address)
    else:
        Address(type=address_type.upper(), address=address, public_key= public_key, ip_address=ip_address).save()


def delete_address(address):
    pass


def update_address(**kwargs):
    pass


def query_address(address):
    pass


if __name__ == "__main__":
    add_address("A11111111111111111111111111111","neo","111111111111111111111111111")