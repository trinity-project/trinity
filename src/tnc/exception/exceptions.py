class TrException(Exception):
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


class ChannelNotExistInDb(TrException):
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
