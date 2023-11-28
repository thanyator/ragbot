




To get started, simply register for an account at https://astra.datastax.com/register and use your Google or GitHub account to sign in, or you can sign up using any email address. The next step is to create a database. 




A demo that demonstrates Astra RAGStax platform, Streamlit interface for a chatbot and DataStax Astra as Vector Store.

Create Astra account, enable RAGStax, create vector database, download the secure bundle and create a token
Create a folder named config
Store the Astra token in json format
Store the secure connect bundle

Create a Streaming tenant and Astra and enable RAGStax on it. 

Install langstream in your computer for CLI

export KAFKA_BOOTSTRAP_SERVERS=""
export KAFKA_USERNAME=""
export KAFKA_PASSWORD=""
export OPEN_AI_ACCESS_KEY=""
export ASTRA_CLIENT_ID=""
export ASTRA_SECRET=""
export ASTRA_TOKEN=""
export ASTRA_DATABASE=
export S3_BUCKET_NAME=
export S3_ENDPOINT=
export S3_ACCESS_KEY=
export S3_SECRET=
export S3_REGION=

ragstack apps deploy ragstax-astra-demo -app app -i instances/astra.yaml -s secrets/secrets.yaml

Review logs using

ragstack apps logs ragstax-astra-demo

Review and Change the code in frontend/chatbot.py based on your config files, keyspace and table names.

export ASTRA_DB_APPLICATION_TOKEN=""
export ASTRA_DB_ID=""
export ASTRA_DB_KEYSPACE=""

streamlit run frontend/chatbot.py