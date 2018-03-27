# -*- coding:utf-8 -*-




from neocore.IO.BinaryWriter import BinaryWriter

from neocore.Fixed8 import Fixed8
from TX.MemoryStream import MemoryStream
from neocore.UInt256 import UInt256



class TransactionType(object):
    ContractTransaction = b'\x80'
    InvocationTransaction = b'\xd1'


class TransactionOutput():
    Value = None  # should be fixed 8
    ScriptHash = None
    AssetId = None

    """docstring for TransactionOutput"""

    def __init__(self, AssetId=None, Value=None, script_hash=None):
        """
        Create an instance.

        Args:
            AssetId (UInt256):
            Value (Fixed8):
            script_hash (UInt160):
        """
        super(TransactionOutput, self).__init__()
        self.AssetId = AssetId
        self.Value = Value
        self.ScriptHash = script_hash

    #        if self.ScriptHash is None:
    #            raise Exception("Script hash is required!!!!!!!!")

    @property
    def Address(self):
        """
        Get the public address of the transaction.

        Returns:
            str: base58 encoded string representing the address.
        """
        return Crypto.ToAddress(self.ScriptHash)

    @property
    def AddressBytes(self):
        """
        Get the public address of the transaction.

        Returns:
            bytes: base58 encoded address.
        """
        return bytes(self.Address, encoding='utf-8')

    def Serialize(self, writer):
        """
        Serialize object.

        Args:
            writer (neo.IO.BinaryWriter):
        """
        writer.WriteUInt256(self.AssetId)
        writer.WriteFixed8(self.Value)
        writer.WriteUInt160(self.ScriptHash)

    def Deserialize(self, reader):
        """
        Deserialize full object.

        Args:
            reader (neo.IO.BinaryReader):
        """
        self.AssetId = reader.ReadUInt256()
        self.Value = reader.ReadFixed8()
        self.ScriptHash = reader.ReadUInt160()
        if self.ScriptHash is None:
            raise Exception("Script hash is required from deserialize!!!!!!!!")

    def ToJson(self):
        """
        Convert object members to a dictionary that can be parsed as JSON.

        Returns:
             dict:
        """
        return {
            'AssetId': self.AssetId.ToString(),
            'Value': self.Value.value,
            'ScriptHash': self.Address
        }


class TransactionInput():
    """docstring for TransactionInput"""

    PrevHash = None
    PrevIndex = None

    def __init__(self, prevHash=None, prevIndex=None):
        """
        Create an instance.
        Args:
            prevHash (UInt256):
            prevIndex (int):
        """
        super(TransactionInput, self).__init__()
        self.PrevHash = prevHash
        self.PrevIndex = prevIndex

    def Serialize(self, writer):
        """
        Serialize object.

        Args:
            writer (neo.IO.BinaryWriter):
        """
        writer.WriteUInt256(self.PrevHash)
        writer.WriteUInt16(self.PrevIndex)

    def Deserialize(self, reader):
        """
        Deserialize full object.

        Args:
            reader (neo.IO.BinaryReader):
        """
        self.PrevHash = reader.ReadUInt256()
        self.PrevIndex = reader.ReadUInt16()

    def ToString(self):
        """
        Get the string representation of the object.

        Returns:
            str: PrevHash:PrevIndex
        """
        return self.PrevHash + ":" + self.PrevIndex

    def ToJson(self):
        """
        Convert object members to a dictionary that can be parsed as JSON.

        Returns:
             dict:
        """
        return {
            'PrevHash': self.PrevHash.ToString(),
            'PrevIndex': self.PrevIndex
        }


class Transaction():
    Type = None

    Version = 0

    Attributes = []

    inputs = []

    outputs = []

    scripts = []

    InventoryType = b'\x01'

    MAX_TX_ATTRIBUTES = 16

    """docstring for Transaction"""

    def __init__(self, inputs=[], outputs=[], attributes=[], scripts=[]):
        """
        Create an instance.
        Args:
            inputs (list): of neo.Core.CoinReference.CoinReference.
            outputs (list): of neo.Core.TX.Transaction.TransactionOutput items.
            attributes (list): of neo.Core.TX.TransactionAttribute.
            scripts:
        """
        super(Transaction, self).__init__()
        self.inputs = inputs
        self.outputs = outputs
        self.Attributes = attributes
        self.scripts = scripts
        self.InventoryType = 0x01  # InventoryType TX 0x01



    @property
    def Scripts(self):
        """
        Get the scripts

        Returns:
            list:
        """
        return self.scripts




    def Serialize(self, writer):
        """
        Serialize object.

        Args:
            writer (neo.IO.BinaryWriter):
        """
        self.SerializeUnsigned(writer)
        writer.WriteSerializableArray(self.scripts)

    def SerializeUnsigned(self, writer):
        """
        Serialize object.

        Args:
            writer (neo.IO.BinaryWriter):
        """
        writer.WriteByte(self.Type)
        writer.WriteByte(self.Version)
        self.SerializeExclusiveData(writer)

        if len(self.Attributes) > self.MAX_TX_ATTRIBUTES:
            raise Exception("Cannot have more than %s transaction attributes" % self.MAX_TX_ATTRIBUTES)

        writer.WriteSerializableArray(self.Attributes)
        writer.WriteSerializableArray(self.inputs)
        writer.WriteSerializableArray(self.outputs)

    def SerializeExclusiveData(self, writer):
        pass



    def ToJson(self):
        """
        Convert object members to a dictionary that can be parsed as JSON.

        Returns:
             dict:
        """
        jsn = {}
        jsn["type"] = self.Type if type(self.Type) is int else int.from_bytes(self.Type, 'little')
        jsn["version"] = self.Version
        jsn["attributes"] = [attr.ToJson() for attr in self.Attributes]
        jsn["vout"] = [out.ToJson() for out in self.outputs]
        jsn["vin"] = [input.ToJson() for input in self.inputs]
        jsn["scripts"] = [script.ToJson() for script in self.scripts]
        return jsn

    def get_tx_data(self):
        ms = MemoryStream()
        w = BinaryWriter(ms)
        self.SerializeUnsigned(w)
        ms.flush()
        tx_data = ms.ToArray().decode()
        return tx_data



class ContractTransaction(Transaction):
    def __init__(self, *args, **kwargs):
        """
        Create an instance.

        Args:
            *args:
            **kwargs:
        """
        super(ContractTransaction, self).__init__(*args, **kwargs)
        self.Type = TransactionType.ContractTransaction


class InvocationTransaction(Transaction):
    Script = None


    def __init__(self, *args, **kwargs):
        """
        Create an instance.

        Args:
            *args:
            **kwargs:
        """
        super(InvocationTransaction, self).__init__(*args, **kwargs)

        self.Type = TransactionType.InvocationTransaction

        self.Gas = Fixed8(0)


    def SerializeExclusiveData(self, writer):
        """
        Serialize object.

        Args:
            writer (neo.IO.BinaryWriter):
        """
        writer.WriteVarBytes(self.Script)
        if self.Version >= 1:
            writer.WriteFixed8(self.Gas)
    def ToJson(self):
        """
        Convert object members to a dictionary that can be parsed as JSON.

        Returns:
             dict:
        """
        jsn = super(InvocationTransaction, self).ToJson()
        jsn['script'] = self.Script.hex()
        return jsn




