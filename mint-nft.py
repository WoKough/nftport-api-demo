#!/usr/bin/python

import sys
import time
import os
import requests

API_URL = 'https://api.nftport.xyz/v0/'
API_KEY = sys.argv[1]
OWNER_ADDRESS = sys.argv[2]
CHAIN = 'polygon'
COLLECTION = 'testavatar collection'
TYPE = 'erc721'
PICFOLDER = sys.argv[3]
PIC_PRE_NAME = 'testavatar'
PICDESCRIP = 'This is testavatar'

def deploy_nft_contract(api_url, api_key, chain, collection, owner_address, types):
    # Deploy your own contract 
    headers = {
        'Authorization': api_key,
        # Already added when you pass json= but not when you pass data=
        'Content-Type': 'application/json',
    }

    json_data = {
        'chain': chain,
        'name': collection,
        'symbol': 'C',
        'owner_address': owner_address,
        'metadata_updatable': False,
        'type': types,
    }

    response = requests.post(api_url + 'contracts', headers=headers, json=json_data)
    try:
        transaction_hash = response.json()['transaction_hash']
    except:
        return -1, ''

    if response.json()['response'] == 'OK':
        return 200, transaction_hash

def get_contract_address(api_url, api_key, chain, transaction_hash):
    # Get the Contract_address
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json',
    }

    params = {
        'chain': chain,
    }

    response = requests.get(api_url + 'contracts/' + transaction_hash, headers=headers, params=params)
    contract_address = ''
    while len(contract_address) == 0:
        count = 0
        try:
            contract_address = response.json()['contract_address']
        except:
            if count > 7200:
                break
            count += 600
            time.sleep(600)
    if len(contract_address) == 0:
        print('can not get contact address\n')
        sys.exit()
    return 200, contract_address

def upload_single_uri(api_url, api_key, pre_name, description, file_item, ipfs_url):
    # Create and upload your NFT metadata file
    headers = {
        'Authorization': api_key,
        # Already added when you pass json= but not when you pass data=
        #'Content-Type': 'application/json',
    }

    json_data = {
        'name': pre_name + ' #' + str(file_item),
        'description': description + ' #' + str(file_item),
        'file_url' : ipfs_url,
    }
    response = requests.post(api_url + 'metadata', headers=headers, json=json_data)

    try:
        metadata_uri = response.json()['metadata_uri']
    except:
        metadata_uri = ''
    return metadata_uri

def upload_single_url(api_url, api_key, filepath, pre_name, description, file_item):
    # Upload your file to IPFS
    headers = {
        'Authorization': api_key,
        # requests won't add a boundary if this header is set when you pass files=
        #'Content-Type': 'multipart/form-data',
        # requests won't add a boundary if this header is set when you pass files=
        #'Content-type': 'multipart/form-data; boundary=---011000010111000001101001',
    }

    files = {
        'file': (pre_name + ' #' + str(file_item), open(filepath, 'rb')),
        #'file': open('/home/fact/NFT/collections/boredapeyachtclub/0.png', 'rb'),
    }

    response = requests.post(api_url + 'files', headers=headers, files=files)
    try:
        ipfs_url = response.json()['ipfs_url']
    except:
        ipfs_url = ''
    
    #print (response.json()['ipfs_url'])
    #sys.exit()
    metadata_uri = ''
    if len(ipfs_url) > 0:
        metadata_uri = upload_single_uri(api_url, api_key, pre_name, description, file_item, ipfs_url)
    return metadata_uri

def upload_pic_to_ipfs(api_url, api_key, folder, pre_name, description):
    uri_list = []
    filelist = os.listdir(folder)
    file_item = 0
    for files in filelist:
        filepath = os.path.join(folder, files)
        metadata_uri = upload_single_url(api_url, api_key, filepath, pre_name, description, file_item)
        if len(metadata_uri) > 0:
            #print (metadata_uri)
            uri_list.append(metadata_uri)
        file_item += 1
    return uri_list

def mint_nft_on_contract(api_url, api_key, chain, owner_address, contract_address, uri_list):
    # Mint NFTs to your contract
    headers = {
        'Authorization': api_key,
        # Already added when you pass json= but not when you pass data=
        # 'Content-Type': 'application/json',
    }
    for metadata_uri in uri_list:
        json_data = {
            'chain': chain,
            'contract_address': contract_address,
            'metadata_uri': metadata_uri,
            'mint_to_address': owner_address,
        }

        response = requests.post(api_url + 'mints/customizable', headers=headers, json=json_data)
        if response.json()['response'] == 'OK':
            print ('%s OK ...' % metadata_uri)

def mint_use_nftport_api():
    result, transaction_hash = deploy_nft_contract(API_URL, API_KEY, CHAIN, COLLECTION, OWNER_ADDRESS, TYPE)
    if result == 200:
        result = -1
        result, contract_address = get_contract_address(API_URL, API_KEY, CHAIN, transaction_hash)
    else:
        print ('deploy nft contract failed\n')
        sys.exit()
    if result == 200:
        #result = -1
        uri_list = upload_pic_to_ipfs(API_URL, API_KEY, PICFOLDER, PIC_PRE_NAME, PICDESCRIP)
    if len(uri_list) != 0:
        mint_nft_on_contract(API_URL, API_KEY, CHAIN, contract_address, uri_list)

if __name__ == '__main__':
  if len(sys.argv) != 4：
    print ("%s api_key owner_address pic_folder" % sys.argv[0])
  else：
    mint_use_nftport_api()
