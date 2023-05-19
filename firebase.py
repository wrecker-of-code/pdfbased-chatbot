from firebase_admin import credentials, firestore
import streamlit as st

db = firestore.client()

doc_ref = db.collection("users").document("user0001")

doc = doc_ref.get()

st.info(doc.id)
st.write(doc.to_dict())

for doc in db.collection("users").get():
    st.write(doc.to_dict())