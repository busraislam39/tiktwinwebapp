import os
from dotenv import load_dotenv
from storages.backends.azure_storage import AzureStorage

load_dotenv()

class AzureMediaStorage(AzureStorage):
    account_name = os.getenv("AZURE_ACCOUNT_NAME")
    account_key = os.getenv("AZURE_ACCOUNT_KEY")
    azure_container = os.getenv("AZURE_CONTAINER")
    expiration_secs = None  # Makes uploaded files publicly accessible
