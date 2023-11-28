import streamlit as st
import langchain
import os
import cassio

from cassandra.cluster import Session
from cassandra.query import PreparedStatement

from langchain.agents.agent_toolkits import create_retriever_tool, create_conversational_retrieval_agent
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.callbacks import StreamlitCallbackHandler
from langchain.schema import BaseRetriever, Document, SystemMessage

from cassio.config import check_resolve_session

# Enable langchain debug mode
langchain.debug = True

cassio.init(
    token=os.environ['ASTRA_DB_APPLICATION_TOKEN'],
    database_id=os.environ['ASTRA_DB_ID'],
    keyspace=os.environ.get('ASTRA_DB_KEYSPACE'),
)


# OpenAI model to use
OPENAI_MODEL = os.getenv("OPENAI_MODEL") or "gpt-4"


class AstraProductRetriever(BaseRetriever):
    session: Session
    embedding: OpenAIEmbeddings
    search_statement: PreparedStatement = None

    class Config:
        arbitrary_types_allowed = True

    def get_relevant_documents(self, query):
        docs = []
        embeddingvector = self.embedding.embed_query(query)
        if self.search_statement is None:
            self.search_statement = self.session.prepare("""
                SELECT
                    filename,
                    text
                FROM finbotastra.bankproccessdocs
                ORDER BY embeddings_vector ANN OF ?
                LIMIT ?
                """)
        query = self.search_statement
        results = self.session.execute(query, [embeddingvector, 5])
        top_products = results._current_rows
        for r in top_products:
            docs.append(Document(
                id=r.filename,
                page_content=r.text,
                metadata={"filename": r.filename,
                          "text":r.text
                          }
            ))

        return docs



@st.cache_resource
def create_chatbot(model="gpt-4"):
    session=check_resolve_session(None)
    llm = ChatOpenAI(model=model, temperature=0, streaming=True)
    embedding = OpenAIEmbeddings()
    # Define tool to query products from Astra DB
    # Instruct OpenAI to use the tool when searching for products
    # and call the tool with English translation of the query
    retriever = AstraProductRetriever(session=session, embedding=embedding)
    retriever_tool = create_retriever_tool(
        retriever,
        "content_retriever",
        "Useful when searching for products and services of hattha bank. \
         When calling this tool, include as much detail as possible, \
         and translate arguments to English.")

    system_message = f"""You are an ai assistant helping customers of a banking institution to answer their queries about their product and services.
    The retriever will help fetch relevant context to answer questions.
    Please try to leverage them in your answer as much as possible.
    Take into consideration that the user is always asking questions relevant to the given context.
    Do not provide information that is not related to provided context.
    All the responses should be the same language as the user used.
    """
    message = SystemMessage(content=system_message)
    agent_executor = create_conversational_retrieval_agent(
        llm=llm, tools=[retriever_tool], system_message=message, verbose=True)
    return agent_executor


if 'history' not in st.session_state:
    st.session_state['history'] = []

st.set_page_config(layout="wide")

chatbot = create_chatbot(OPENAI_MODEL)

if st.button("Clear chat history"):
    st.session_state['history'] = []
    chatbot.memory.clear()

# Display chat messages from history on app rerun
for (query, answer) in st.session_state['history']:
    with st.chat_message("User"):
        st.markdown(query)
    with st.chat_message("Bot"):
        st.markdown(answer)

prompt = st.chat_input(placeholder="Ask RAG Bot")
if prompt:
    # Display user message in chat message container
    with st.chat_message("User"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("Bot"):
        st_callback = StreamlitCallbackHandler(st.container())
        result = result = chatbot.invoke({
            "input": prompt,
            "chat_history": st.session_state['history']
        }, config={"callbacks": [st_callback]})
        st.session_state['history'].append((prompt, result["output"]))
        st.markdown(result["output"])