from pinecone import Pinecone, PodSpec
import os

from dotenv import load_dotenv
load_dotenv()

PINECONE_KEY, PINECONE_INDEX_NAME = os.getenv(
    'PINECONE_API_KEY'), os.getenv('PINECONE_INDEX_NAME')

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_KEY)

# Delete index
pc.delete_index(PINECONE_INDEX_NAME)

# # Create empty index
# pc.create_index(
#     name="film-bot-index",
#     dimension=1536,
#     metric="cosine",
#     spec=PodSpec(
#         environment="gcp-starter"
#     )
# )
