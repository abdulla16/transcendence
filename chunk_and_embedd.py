import boto3


def chunk_text(text, chunk_size):
    """Split the text into chunks of up to `chunk_size` characters."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def embed_text_chunks(text, chunk_size=512):
    # Initialize the Bedrock client with a specified region
    client = boto3.client('sagemaker-runtime')
    boto3_session = boto3.session.Session()
    region_name = boto3_session.region_name

    bedrock_agent_client = boto3_session.client('bedrock-agent', region_name=region_name)

    # Endpoint for the Titan Text Embeddings V2 model
    endpoint_name = 'amazon.titan-embed-text-v1'

    # Split the text into chunks
    text_chunks = chunk_text(text, chunk_size)

    embeddings = []
    for chunk in text_chunks:
        # Prepare the input payload
        payload = f'{{"inputText": "{chunk}"}}'

        # Invoke the endpoint
        response = client.invoke_endpoint(
            TargetModel=endpoint_name,
            Body=payload.encode('utf-8'),
            ContentType='application/json'
        )

        # Process the response and extract the embeddings
        import json
        result = json.loads(response['Body'].read().decode('utf-8'))
        embeddings.append(result)

    return embeddings


# Example usage
text = "Your long text goes here. This text will be split into chunks and each chunk will be embedded."
embeddings = embed_text_chunks(text)
print(embeddings)