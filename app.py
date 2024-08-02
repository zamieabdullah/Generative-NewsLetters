import streamlit as st
from generate import generate

blog = None

while blog == None:
    blog = generate()

st.title(blog["title"])
st.markdown(blog["content"])