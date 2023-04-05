import requests
import uuid

rpc_network = "http://127.0.0.1:17076"
session = requests.Session()

def key_expand(key):
    return session.post(rpc_network, json={
        "action": "key_expand",
        "key": key
    }).json()

def wallet_create(key):
    return session.post(rpc_network, json={
        "action": "wallet_create",
        "seed": key,
    }).json()

def accounts_create(wallet, count=1):
    return session.post(rpc_network, json={
        "action": "accounts_create",
        "wallet": wallet,
        "count": count
    }).json()

def receive(wallet, account, block):
    return session.post(rpc_network, json={
        "action": "receive",
        "wallet": wallet,
        "account": account,
        "block": block
    }).json()

def account_info(account):
    return session.post(rpc_network, json={
        "action": "account_info",
        "representative": "true",
        "account": account
    }).json()

def wallet_info(wallet):
    return session.post(rpc_network, json={
        "action": "wallet_info",
        "wallet": wallet
    }).json()

def ledger(account, count):
    return session.post(rpc_network, json={
        "action": "ledger",
        "account": account,
        "count": count
    }).json()

def wallet_history(wallet):
    return session.post(rpc_network, json={
        "action": "wallet_history",
        "wallet": wallet
    }).json()

def account_list(wallet):
    return session.post(rpc_network, json={
        "action": "account_list",
        "wallet": wallet
    }).json()

def send(wallet, source, destination, amount):
    return session.post(rpc_network, json={
        "action": "send",
        "wallet": wallet,
        "source": source,
        "destination": destination,
        "amount": str(amount),
        "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, 'nanoswap.finance'))
    }).json()

def receivable(account, count=1, threshold=1000000000000000000000000):
    return session.post(rpc_network, json={
        "action": "receivable",
        "account": account,
        "count": count,
        "threshold": threshold,
        "source": "true"
    }).json()

def block_create(previous, account, representative, balance, link, key):
    return session.post(rpc_network, json={
        "action": "block_create",
        "json_block": "true",
        "type": "state",
        "previous": previous,
        "account": account,
        "representative": representative,
        "balance": balance,
        "link": link,
        "key": key
    }).json()

# def process():
#     return session.post(rpc_network, json={
#         "action": "process",
#         "json_block": "true",
#         "subtype": "open",
#         "block": 
#         "type": "state",
#         "account": "nano_1rawdji18mmcu9psd6h87qath4ta7iqfy8i4rqi89sfdwtbcxn57jm9k3q11",
#         "previous": "0000000000000000000000000000000000000000000000000000000000000000",
#         "representative": "nano_1stofnrxuz3cai7ze75o174bpm7scwj9jn3nxsn8ntzg784jf1gzn1jjdkou",
#         "balance": "100",
#         "link": "5B2DA492506339C0459867AA1DA1E7EDAAC4344342FAB0848F43B46D248C8E99",
#         "link_as_account": "nano_1psfnkb71rssr34sisxc5piyhufcrit68iqtp44ayixnfnkas5nsiuy58za7",
#         "signature": "903991714A55954D15C91DB75CAE2FBF1DD1A2D6DA5524AA2870F76B50A8FE8B4E3FBB53E46B9E82638104AAB3CFA71CFC36B7D676B3D6CAE84725D04E4C360F",
#         "work": "08d09dc3405d9441"
#     }).json()
