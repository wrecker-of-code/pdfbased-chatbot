from dotenv import load_dotenv
from pypdf import PdfReader

# Langchain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS, Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback

import streamlit as st
import os
from streamlit_chat import message


load_dotenv()


def main():
    # api_key = os.getenv('OPENAI_API_KEY')

    st.set_page_config(page_title='KPMG Q&A Tool', page_icon=':question:')
    st.sidebar.title('KPMG Q&A Tool')

    st.title('KPMG Q&A Tool')

    uploaded_file = st.file_uploader('Upload your file', type=['pdf'])

    container = st.container()

    
    if uploaded_file is not None:
        pdf = PdfReader(uploaded_file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

        with container:
            with st.expander(f"Inhalt von {uploaded_file.name}"):
                st.write(text)

        
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len
        )

        chunks = text_splitter.split_text(text)

        # embeddings
        embeddings = OpenAIEmbeddings()
        knowledge_base = FAISS.from_texts(chunks, embeddings)


        # setup_chatbot(text)
        

        question = st.text_input(label='Ask me anything 👇', placeholder='What is the main summary of the document?', key='search')

        if question:
            with container:
                message(question, is_user=True)

            docs = knowledge_base.similarity_search(question)

            # llm = OpenAI(model_name="gpt-3.5-turbo")
            llm = ChatOpenAI(model_name="gpt-3.5-turbo")
            chain = load_qa_chain(llm, chain_type="map_reduce")
            with get_openai_callback() as cb:
                print("Chat")
                response = chain.run(input_documents=docs, question=question)
                print(cb)
            
            with container:
                message(response)


def setup_chatbot(text):
    embeddings = OpenAIEmbeddings()

    vector_db = Chroma.from_texts(text, embeddings, persist_directory=".")
    vector_db.persist()

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    pdf_qa = ConversationalRetrievalChain.from_llm(
        OpenAI(temperature=0.2, model_name="gpt-3.5-turbo"), 
        vector_db.as_retriever(), 
        memory=memory
    )


   


if __name__ == '__main__':
    main()