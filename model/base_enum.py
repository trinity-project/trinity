# --*-- coding : utf-8 --*--
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
from enum import IntEnum


class EnumChainType(IntEnum):
    TNC = 0
    NEO = 0x4

    # could be expanded in the future


class EnumAssetType(IntEnum):
    TNC = 0
    NEO = 0x4


class EnumNodeState(IntEnum):
    ACTIVE = 0
    INACTIVE = 0xFF


class EnumChannelState(IntEnum):
    INIT = 0
    OPENING = 0x10  # in wait response state
    OPENED = 0x11

    SETTLING = 0x20
    SETTLED = 0x21

    CLOSING = 0x30
    CLOSED = 0x31


class EnumStatusCode(IntEnum):
    OK = 0

    InvalidDatabaseConnection = 0x10

    PrimaryKeyNotFound = 0x20
    PrimaryKeyNotFoundInAddingNewItem = 0x21
    PrimaryKeyIsDuplicated = 0x22
    PrimaryKeyInsertWithException = 0x23

    DBDeletedWithoutAnyItems = 0x30
    DBDeletedWithDangerousFilters = 0x31

    DBQueryWithoutMatchedItems = 0x40

    DBUpdatedButNoMatchedItemsOK = 0x50
    DBUpdatedPartOfItemsOK = 0x51
    DBUpdatedWithDangerousFilters = 0x52

    NOK = 0xFF

