import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json

load_dotenv()

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

################################################################################
# Contract Helper function:
# 1. Loads the contract once using cache
# 2. Connects to the contract using the contract address and ABI
################################################################################


# Cache the contract on load
@st.cache(allow_output_mutation=True)
# Define the load_contract function
def load_contract():
    
    # Load Art Gallery ABI
    with open(Path('./contracts/compiled/dogregistry_abi.json')) as f:
        registry_abi = json.load(f)

    # Set the contract address (this is the address of the deployed contract)
    contract_address = os.getenv("DOG_REGISTRY_CONTRACT")

    # Get the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=registry_abi
    )
    # Return the contract from the function
    return contract


# Load the contract
contract = load_contract()


# Dog Registry app structure 

image = Image.open('./DogRegistryChain.png')
st.image(image)

# Adding sidebar for ERC721 token name
with st.sidebar:
    image = Image.open('./dogRegistryLOGO.png')
    st.image(image)
    if st.button("name"):
        receipt = contract.functions.name()().call()
        # view receipt
        st.write(receipt)

# Adding sidebar for ERC721 token symbol
with st.sidebar:
    if st.button("symbol"):
        receipt = contract.functions.symbol().call()
        # view receipt
        st.write(receipt)

# Adding sidebar for ERC721 total supply call
with st.sidebar:
    if st.button("TotalSuppy"):
        receipt = contract.functions.totalSupply().call()
        # view receipt
        st.write(receipt)

# Adding sidebar to select accounts to interface with streamlit app and functions
with st.sidebar:
    st.markdown("# Select account")
    accounts = w3.eth.accounts
    account = accounts[0]
    selected_account = st.selectbox("Select Account", options=accounts)

################################################################################
# Add Broker Account
################################################################################

# Adding broker account
st.markdown("## Add Government Authority")
st.markdown('##### NGO adds Government Authority')
broker_address = st.text_input("Government Authority Address")
broker_id = st.text_input("Government Authority ID")

# Add broker button
if st.button("Add Government Authority"):
    tx_hash = contract.functions.addBroker(broker_address, broker_id).transact({'from': selected_account, 'gas': 1000000})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.write(dict(receipt))

################################################
# Add Veterinarian Doctor
################################################

st.markdown("## Add Veterinarian Doctor")
st.markdown('##### Government Authority adds Doctor')
veterinarian_address = st.text_input("Veterinarian  Address")
veterinarian_id = st.text_input("Animal Veterinarian  ID")

# Add Veterinarian button
if st.button("Add Veterinarian Doctor"):
    tx_hash = contract.functions.addVeterinarianDoctor(veterinarian_address, veterinarian_id).transact({'from': selected_account, 'gas': 1000000})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.write(dict(receipt))

################################################
# Add Animal Breeder
################################################

st.markdown("## Add Animal Breeder")
st.markdown('##### Government Authority adds Animal Breeder')
breeder_address = st.text_input("Breeder Address")
breeder_id = st.text_input("Animal Breeder ID")

# Add breeder button
if st.button("Add Animal Breeder"):
    tx_hash = contract.functions.addDogBreeder(breeder_address, breeder_id).transact({'from': selected_account, 'gas': 1000000})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.write(dict(receipt))


##########################################################
# Helper functions to pin files and json to Pinata
##########################################################

def pin_dog(dog_name, dog_file):
    # Pin the file to IPFS with Pinata
    ipfs_file_hash = pin_file_to_ipfs(dog_file.getvalue())

    # Build a token metadata file for the dog
    token_json = {
        "name": dog_name,
        "image": ipfs_file_hash
    }
    json_data = convert_data_to_json(token_json)

    # Pin the json to IPFS with Pinata
    json_ipfs_hash = pin_json_to_ipfs(json_data)

    return json_ipfs_hash, token_json

################################################
# Register Animal
################################################

st.markdown("## Register New Animal")
st.markdown('##### Animal Breeder adds Animal')
dog_owner = st.text_input("Enter the Animal owner")
AnimalID = st.text_input("Enter the Animal ID")
breed = st.text_input("Enter the Animal breed")
dame = st.text_input("Enter the dame ID")
sire = st.text_input("Enter the Animal sire ID")
initial_value = st.number_input("Enter Animal sale Value", value=0, step=1 )

# Streamlit File uploader
file = st.file_uploader("Upload Animal", type=["jpg", "jpeg", "png"])

if st.button("Register New Animal"):
    dog_ipfs_hash, token_json = pin_dog(AnimalID, file)
    dog_uri = f"https://gateway.pinata.cloud/ipfs/{dog_ipfs_hash}"

    tx_hash = contract.functions.registerDog(w3.to_checksum_address(dog_owner),AnimalID,breed, dame,sire,initial_value,dog_uri,token_json["image"]).transact({'from': selected_account, 'gas': 1000000})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.write(dict(receipt))

################################################
# Add Animal Health Report
################################################
tokens = contract.functions.totalSupply().call()

st.markdown("## Add Animal Health Report")
st.markdown('##### Doctor adds Health Report')
Animal_id = st.selectbox("Choose a Animal Token ID", list(range(tokens)))
Animal_id = st.text_input("Animal ID")
vet_address = st.text_input("Vet  Address")
vet_id = st.text_input("Vet  ID")
remarks = st.text_input("Add Remarks")

# Add health report button
if st.button("Add Health Report"):
    tx_hash = contract.functions.addAnimalReport(Animal_id, vet_address, vet_id, remarks).transact({'from': selected_account, 'gas': 1000000})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.write(dict(receipt))


# Helper function to pin appraisal report
def pin_appraisal_report(report_content):
    json_report = convert_data_to_json(report_content)
    report_ipfs_hash = pin_json_to_ipfs(json_report)
    return report_ipfs_hash

################################################################################
# Appraise Dog
################################################################################

st.markdown("## Appraise Animal")
st.markdown("##### New Animal owner appraises Animal value")
dog_token_id = st.selectbox("Choose Animal Token ID", list(range(tokens)))
new_appraisal_value = st.text_input("Enter the new appraisal amount")
appraisal_report_content = st.text_area("Enter details for the Appraisal Report")

if st.button("Appraise Animal"):

    # Make a call to the contract to get the image uri
    image_uri = str(contract.functions.imageUri(dog_token_id).call())
    
    # Use Pinata to pin an appraisal report for the report content
    appraisal_report_ipfs_hash =  pin_appraisal_report(appraisal_report_content+image_uri)

    # Copy and save the URI to this report for later use as the smart contract’s `reportURI` parameter.
    report_uri = f"https://gateway.pinata.cloud/ipfs/{appraisal_report_ipfs_hash}"

    tx_hash = contract.functions.newAppraisal(
        dog_token_id,
        int(new_appraisal_value),
        report_uri,
        image_uri

    ).transact({"from": selected_account})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    st.write(dict(receipt))
st.markdown("---")

################################################################################
# Get Appraisals
################################################################################

st.markdown("## Get the appraisal report history")
dog_token_id = st.number_input("Animal Token ID", value=0, step=1)
if st.button("Get Appraisal Reports"):
    appraisal_filter = contract.events.Appraisal.createFilter(
        fromBlock=0, argument_filters={"tokenId": dog_token_id}
    )
    reports = appraisal_filter.get_all_entries()
    if reports:
        for report in reports:
            report_dictionary = dict(report)
            st.markdown("### Appraisal Report Event Log")
            st.write(report_dictionary)
            st.markdown("### Pinata IPFS Report URI")
            report_uri = report_dictionary["args"]["reportURI"]
            report_ipfs_hash = report_uri[7:]
            image_uri = report_dictionary["args"]["image"]
            st.markdown(
                f"The report is located at the following URI: "
                f"{report_uri}"
            )
            st.markdown("### Appraisal Event Details")
            st.write(report_dictionary["args"])
            st.image(f'https://gateway.pinata.cloud/ipfs/{report_dictionary["args"]["image"]}')
    else:
        st.write("This Animal has no new appraisals")


# Adding sidebar button to check broker address, returns true if address given is a broker
with st.sidebar:
    transfer_token = st.markdown("# Check Broker")
    address = st.text_input("Check if Broker address is true")
    if st.button("Check broker address"):
        receipt = contract.functions.isBroker(address).call()
        # view receipt
        st.write(receipt)

# Adding sidebar button to check vet address, returns true if address given is veterenian doctor
with st.sidebar:
    transfer_token = st.markdown("# Check Vet")
    address = st.text_input("Check if Vet address is true")
    if st.button("Check vet address"):
        receipt = contract.functions.isVeterinarianDoctor(address).call()
        # view receipt
        st.write(receipt)

# Adding sidebar button to check breeder address, returns true is address given is a breeder
with st.sidebar:
    transfer_token = st.markdown("# Check Breeder")
    address = st.text_input("Check if Breeder address is true")
    if st.button("Check breeder address"):
        receipt = contract.functions.isDogBreeder(address).call()
        # view receipt
        st.write(receipt)

# Adding button to check metadata for given Animal token id
with st.sidebar:
    transfer_token = st.markdown("# Check Animal")
    token_id = st.number_input("Animal token_ID", value=0, step=1)
    if st.button("Animal Metadata"):
        receipt = contract.functions.dogCollection(token_id).call()
        # view receipt
        st.write(receipt)

# Adding button to tranfer ownership of a Animal ERC721 token (Animal NFT)
with st.sidebar:
    transfer_token = st.markdown("# Transfer Animal")
    from_address = st.text_input("Owner Address")
    to_address = st.text_input("Receiver Address")
    token_id = st.number_input("Animal token ID", value=0, step=1)
    if st.button("Transfer Animal"):
        tx_hash = contract.functions.safeTransferFrom(w3.to_checksum_address(from_address), w3.to_checksum_address(to_address), token_id).transact({'from': selected_account, 'gas': 1000000})
        # view receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        st.write("Transaction receipt mined:")
        st.write(dict(receipt))
