import streamlit as st
from generate import generate
import os

print("Current Working Directory:", os.getcwd())
blog = None
# Show a spinner while waiting for the blog to generate
with st.spinner("Waiting for blog to load..."):
    while blog == None:
        blog = generate()
        print(blog["title"])

# Display the generated blog
# st.title(blog["title"])
st.markdown(blog["content"])