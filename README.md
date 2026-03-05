Here is how to navigate this messy code:

Folders:

data: Includes all data that is useful to keep, including cwallet addresses (from different networks), addresses <> user id connections,
user id <> pii connections.

scripts: All the scripts involved in the process.

addresses: Scripts that spesifically use public api to extract addresses of cwallet users from the blockchain. There are couple of scripts 
because there are couple of coins/networks. More will be added in the future if necessary.

info: Things I need to remember.



Files:

scripts:
main: The beginnig of the script. This is run after we already got candidate addresses from running the scripts in the addresses folder.
userIdExtraction function is responsible to create addresses <> user id connections.
userDataExtraction function is responsible to create user id <> pii connections.

script: has userIdExtraction and userDataExtraction functions. This are responsible to read the candidate cwallet addresses, and create a pool of workers. Eahc worker will either perform a transaction (in the case of userIdExtraction), or call account/other/user endpoint.

attack: cointain mainly functions that are responsible to send requests to different endpoint to cwallet. And also has executeFullTransaction function which execute all the transaction proccess.

post: has the post function, which sends a post request to cwallet. This file also contain the encryption and decryption methods.

parse: File parsing and CSV parsing functions

coin: There are different coin related data that is needed in some requests to some cwallet endpoints.

utils: general helpful functions

test: IGNORE (used it to test for some stuff)



addresses:
bnb_covalent: extracting addresses from the BEP20 network.
btc_explorer: extracting addresses from the bitcoin blockchain.
eth_alchemy: extracting addresses from the ERC20 network.



data:
unique_senders_alchemy: candidate cwallet addresses that used ERC20
unique_senders_covalent: candidate cwallet addresses that used BEP20
btc_new_addresses: candidate cwallet addresses that used bitcoin blockchain.
results_eth: unique_senders_alchemy addresses <> user id connections.
results_eth_two: unique_senders_alchemy addresses <> pii connections.