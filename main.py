from langchain.callbacks import get_openai_callback
from chatbot import PdfChatbot
from dotenv import load_dotenv
import streamlit as st
from streamlit_chat import message
from streamlit_option_menu import option_menu
from styles import *
import base64
import pyautogui

import firebase_admin
from firebase_admin import auth




load_dotenv()


# daily_cost = 0


@st.cache_resource
def setup_chain(file):
    kpmg_chatbot = PdfChatbot()

    kpmg_chatbot.read_pdf(file)
    kpmg_chatbot.split_and_store_data()
    chain = kpmg_chatbot.setup_chatbot()

    return chain


def show_pdf(file_path):
    with open(file_path,"rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# def login_modal():
#     email = st.text_input("Email")
#     password = st.text_input("Password", type="password")
#     if st.button("Login", key="login-button"):
#         # Perform login logic here
#         st.success("Logged in successfully!")


# def signup_modal():
#     email = st.text_input("Email")
#     password = st.text_input("Password", type="password")
#     confirm_password = st.text_input("Confirm Password", type="password")
#     if st.button("Sign Up", key="signup-button"):
#         # Perform signup logic here
#         st.success("User created successfully!")


def main():
    # global daily_cost
    # Set page configuration.
    st.set_page_config(page_title='KPMG Q&A Tool', page_icon=':question:')
    st.markdown(style_spinner, unsafe_allow_html=True)
    st.markdown(style_text_input, unsafe_allow_html=True)
    # st.markdown(style_avatar, unsafe_allow_html=True)
    # st.markdown(style_answer, unsafe_allow_html=True)
    # st.markdown(style_auth_buttons, unsafe_allow_html=True)


    sidebar = st.sidebar
    with sidebar:
        # if st.button("Login", key="open-login"):
        #     st.markdown("""---""")
        #     login_modal()

        # if st.button("Sign Up", key="open-signup"):
        #     st.markdown("""---""")
        #     signup_modal()


        st.title('KPMG Q&A Tool')
        st.write('This is a tool that will help you to ask questions about the document and get the answer from the chatbot.')
        
        new_session = st.button("Start new session...")
        if new_session:
            pyautogui.hotkey('ctrl', 'f5')

        
        st.warning('Uploaded files will be shown here:')

        file_placeholder = st.container()

    st.title('KPMG Q&A Tool')


    upload_placeholder = st.empty()
    uploaded_file = upload_placeholder.file_uploader('Upload your file', type=['pdf'])
    if uploaded_file:
        with open(f"files/{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())

        chain = setup_chain(f"files/{uploaded_file.name}")

        with st.spinner():
            st.info(f"Showing file {uploaded_file.name}")
            with st.expander("Show Preview"):
                st.success("Preview of the document")
                show_pdf(f"files/{uploaded_file.name}")

        with file_placeholder:
            st.success(uploaded_file.name)
            upload_placeholder.empty()


        st.write("---")

        if "generated" not in st.session_state:
            st.session_state["generated"] = []

        if "past" not in st.session_state:
            st.session_state["past"] = []

            with st.spinner("Starting chatbot..."):
                with get_openai_callback() as cb:
                    response = chain.run(question="Give a short introduction to the document and give three questions that can be asked about the document as bullet points (make the bullet points easily visible).")

                    # daily_cost += cb.total_cost

                    st.session_state.generated.insert(0, response)



        question = st.text_input(label='Ask me anything 👇', placeholder='', key='search')

        spinner = st.spinner(text="Generating answer...")


        if question:
            with spinner:
                with get_openai_callback() as cb:
                    response = chain.run(question=question)

                # daily_cost += cb.total_cost

                st.session_state.past.insert(0, question)
                st.session_state.generated.insert(0, response)

        if st.session_state["generated"]:
            for i in range(len(st.session_state["generated"]) - 1, -1, -1):
                try:
                    message(st.session_state["past"][i], is_user=True, key=str(i) + "_user", avatar_style="initials", seed="TP")
                except:
                    pass
                message(st.session_state["generated"][i], key=str(i), avatar_style="bottts", seed="Aneka")





if __name__ == '__main__':
    main()