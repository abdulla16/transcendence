import os
import uuid

import boto3


def chunk_text(text, chunk_size):
    """Split the text into chunks of up to `chunk_size` characters."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def embed_text_chunks(user, chunk_size=512):

    # Ingest strategy - How to ingest data from the data source
    chunkingStrategyConfiguration = {
        "chunkingStrategy": "FIXED_SIZE",
        "fixedSizeChunkingConfiguration": {
            "maxTokens": 512,
            "overlapPercentage": 20
        }
    }
    bucket_name = 'transcendence-bedrock-kb-us-west-2-712521394861'
    # The data source to ingest documents from, into the OpenSearch serverless knowledge base index
    s3Configuration = {
        "bucketArn": f"arn:aws:s3:::{bucket_name}",
        "inclusionPrefixes": [f"{user}"] # you can use this if you want to create a KB using data within s3 prefixes.
    }
    data_root = f"./{user}/"
    s3_client = boto3.client("s3")

    def uploadDirectory(path, bucket_name):
        for root, dirs, files in os.walk(path):
            for file in files:
                s3_client.upload_file(os.path.join(root, file), bucket_name, os.path.join(user, file))

    uploadDirectory(data_root, bucket_name)
    # Initialize the Bedrock client with a specified region
    client = boto3.client('sagemaker-runtime')
    boto3_session = boto3.session.Session()
    region_name = boto3_session.region_name
    bedrock_agent_client = boto3_session.client('bedrock-agent', region_name=region_name)
    kb_id = 'IX9OJRTSSW'
    create_ds_response = bedrock_agent_client.create_data_source(
        name=f'bedrock-sample-knowledge-base-{uuid.uuid4()}',
        description='testiong',
        knowledgeBaseId=kb_id,
        dataSourceConfiguration={
            "type": "S3",
            "s3Configuration": s3Configuration
        },
        vectorIngestionConfiguration={
            "chunkingConfiguration": chunkingStrategyConfiguration
        }
    )
    ds = create_ds_response["dataSource"]
    start_job_response = bedrock_agent_client.start_ingestion_job(knowledgeBaseId=kb_id,
                                                                  dataSourceId=ds["dataSourceId"])


# Example usage
# text = "Your long text goes here. This text will be split into chunks and each chunk will be embedded."
# embeddings = embed_text_chunks('abdul')
# print(embeddings)