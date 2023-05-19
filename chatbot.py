from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import PyPDFLoader
from langchain.chains.llm import LLMChain
from langchain.callbacks.streamlit import StreamlitCallbackHandler
from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT, QA_PROMPT
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
import openai

from pypdf import PdfReader
from dotenv import load_dotenv



# Construct a ConversationalRetrievalChain with a streaming llm for combine docs
# and a separate, non-streaming llm for question generation


load_dotenv()


class PdfChatbot():
    def __init__(self):
        pass


    def read_pdf(self, file="files/ED_ESRS_E1.pdf"):
        self.loader = PyPDFLoader(file)
        self.pages = self.loader.load_and_split()

        return self.pages


    def split_and_store_data(self, chunk_size=1000):
        text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=0)
        documents = text_splitter.split_documents(self.pages)

        embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma.from_documents(documents, embeddings)

        return self.vectorstore
    

    def setup_chatbot(self):
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        llm = ChatOpenAI(temperature=0.5)
        streaming_llm = ChatOpenAI(streaming=True, callbacks=BaseCallbackManager(handlers=[StreamingStdOutCallbackHandler, StreamlitCallbackHandler]), temperature=0.5)

        question_generator = LLMChain(llm=llm, prompt=CONDENSE_QUESTION_PROMPT)
        doc_chain = load_qa_chain(streaming_llm, chain_type="stuff", prompt=QA_PROMPT)

        self.qa = ConversationalRetrievalChain(
            retriever=self.vectorstore.as_retriever(),
            combine_docs_chain=doc_chain,
            question_generator=question_generator,
            memory=memory
        )
        
        return self.qa
    
        
