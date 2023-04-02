from utils import nano
import subprocess

class Account():
    
    def __init__(self, key):
        # add key data
        self.key = key
        key_expand_response = nano.key_expand(key)
        self.account = key_expand_response['account']
        
        # create the wallet
        wallet_create_response = nano.wallet_create(self.key)
        print(wallet_create_response)
        assert 'error' not in wallet_create_response
        self.wallet = wallet_create_response['wallet']
        
        # create the account
        accounts_create_response = nano.accounts_create(self.wallet)
        assert 'error' not in accounts_create_response
        
    
    def send(self, destination, amount):
#         assert balance(self.wallet) >= amount
       nano.send(self.wallet, self.account, destination, amount)
    
    @staticmethod
    def generate_private_key():
        command = "LC_ALL=C cat /dev/urandom | LC_ALL=C tr -dc '0-9A-F' | LC_ALL=C head -c${1:-64}"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        return process.stdout.read()


    @staticmethod
    async def receivable_promise(wallet, account):
        while True:
            receiveable_response = nano.receiveable(account)
            print(receiveable_response)
            
            # todo: add block
            
            blocks = receiveable_response["blocks"]
            print(blocks)
            if blocks:
                block = list(blocks.keys())[0]
                break
            
            time.sleep(10)

        nano.receive(wallet, account, block)

    @staticmethod
    def balance(wallet):
        account_info_response = nano.account_info(wallet)
        assert 'error' not in account_info_response
        return account_info_response['balance']
