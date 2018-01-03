using Neo.SmartContract.Framework;
using Neo.SmartContract.Framework.Services.Neo;
using Neo.SmartContract.Framework.Services.System;
using System;
using System.ComponentModel;
using System.Numerics;
using System.Collections.Generic;



namespace Neo.SmartContract
{
    public class Lock : Framework.SmartContract
    {
        [DisplayName("transfer")]
        public static event Action<byte[], byte[], BigInteger> Transferred;

        [DisplayName("refund")]
        public static event Action<byte[], BigInteger> Refund;

        public static Object Main(string operation, params object[] args)
        {
            if (Runtime.Trigger == TriggerType.Verification)
            {
                return false;
            }
            else if (Runtime.Trigger == TriggerType.Application)
            {
                if (operation == "lock") return Lock(args);
                if (operation == "unlock") return Unlock();
                if (operation == "channle_info") return ChannelInfo();

                return false;
            }
        }

        public static bool Lock(byte[] args)
        {
            if (args.Length != 4) return false;
            byte[] channel_name = args[0];
            byte[] sender_address = args[1];
            byte[] reciever_address = args[2];
            byte[] deposit = args[3];
            byte state = 1;
            ArrayList channel_info = new ArrayList();
            channel_info.Add(channel_name);
            channel_info.Add(sender_addres);
            channel_info.Add(reciever_address);
            channel_info.Add(deposit);
            channel_info.Add(state);

            Storage.Put(Storage.CurrentContext, args[0], channel_info);
            if (!transer_deposit_to_lock(deposit)) return false;
            return  Neo.Runtime.Notify;
        }

        public static bool Unlock(byte[] args)
        {
            if (args.Length != 3) return false;
            byte[] channel_name = args[0];
            byte[] sender_sig = args[1];
            byte[] reciever_sig = args[2];
          
            ArrayList channel_info = Storage.Put(Storage.CurrentContext, args[0]);
            if (channel_info.Count() == 0) return false;
            channel_info[4] =0;
            if (!settle_channle(channel_name, sender_sig, reciever_sig)) return false;
            return Neo.Runtime.Notify;
        }

        public static bool transer_deposit_to_lock(byte[] deposit)
        {
            return true;
        
        }

        public static bool settle_channle(byte[] channel_name, byte[] sender_sig, byte[] reciever_sig)
        {
            return true;
        }

    }
    
}
