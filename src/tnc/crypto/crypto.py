from typing import List, Tuple, Any
import pickle


def dic2btye(file_handler, **kwargs):
    """

    :param kwargs:
    :return:
    """
    return pickle.dump(kwargs, file_handler)


def crypto_channel(file_handler, **kwargs):
    """
    :param kwargs:
    :return:
    """
    return dic2btye(file_handler, **kwargs)

def uncryto_channel(file_handler):
    """

    :param file_handler:
    :return:
    """
    return byte2dic(file_handler)

def byte2dic(file_hander):
    """

    :param file_hander:
    :return:
    """
    return pickle_load(file_hander)

def pickle_load(file):
    """

    :param file:
    :return:
    """
    pickles = []
    while True:
        try:
            pickles.append(pickle.load(file))
        except EOFError:
            return pickles
