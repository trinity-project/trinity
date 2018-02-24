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


class TrException(Exception):
    def __init__(self, *value):
        self.value = value

    def __str__(self):
        return repr(self) + repr(self.value)


class UnKnownType(TrException):
    pass


class NoChannelFound(TrException):
    pass


class InvalidBalanceAmount(TrException):
    pass


class InvalidBalanceProof(TrException):
    pass


class ChannelDBAddFail(TrException):
    pass


class ChannelFileNoExist(TrException):
    pass


class ChannelExistInDb(TrException):
    pass


class ChannelNotExist(TrException):
    pass


class ChannelClosed(TrException):
    pass


class ChannelSettling(TrException):
    pass


class ChannleNotInCloseState(TrException):
    pass


class ChannelDBUpdateFail(TrException):
    pass


class ChannelNotInOpenState(TrException):
    pass


class NoBalanceEnough(TrException):
    pass


class ChannelExist(TrException):
    pass


class NoOpenChannel(TrException):
    pass


class AddressError(TrException):
    pass


class InsufficientConfirmations(TrException):
    pass


class NoBalanceProofReceived(TrException):
    pass


class StateFileException(TrException):
    pass


class StateContractAddrMismatch(StateFileException):
    pass


class StateReceiverAddrMismatch(StateFileException):
    pass


class StateFileLocked(StateFileException):
    pass


class InsecureStateFile(StateFileException):
    pass


class NetworkIdMismatch(StateFileException):
    pass


class TransCanNotBelessThanZ(StateFileException):
    pass

class QureyRoleNotCorrect(TrException):
    pass