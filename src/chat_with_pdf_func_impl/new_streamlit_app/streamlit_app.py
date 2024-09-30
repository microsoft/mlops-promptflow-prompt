import os
import streamlit as st
import requests
import json
import time

st.title("Chat with pdf RAG example with Streamlit and Azure Durable Functions")

if 'pdf_url' not in st.session_state:
    st.session_state.pdf_url = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Step 1: Provide PDF URL
st.title("Provide a PDF URL")
pdf_input_url = st.text_input("Enter the URL of the PDF file:")

if st.button("Submit PDF URL"):
    if pdf_input_url:
        st.session_state.pdf_url = pdf_input_url
        st.success(f"PDF URL has been saved: {st.session_state.pdf_url}")
    else:
        st.error("Please enter a valid PDF URL")

if st.session_state.pdf_url:
    st.write(f"Current PDF URL: {st.session_state.pdf_url}")
else:
    st.info("No PDF URL provided yet.")

# Step 2: Input for triggering the Durable Function
input_question = st.text_input("Enter the question", "example")

if st.button("Run Durable Function"):
    # url = "http://localhost:7071/api/chatwithpdfinvoke"
    url = os.environ.get("DURABLE_FUNCTION_URL")

    headers = {
        "Content-Type": "application/json",
        "Traceparent": "ok"
    }
    data = {
        "pdf_url": st.session_state.pdf_url,
        "question": input_question,
        "chat_history": st.session_state.chat_history
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Ensure the request succeeded
        response_data = response.json()

        if 'statusQueryGetUri' not in response_data:
            st.error("statusQueryGetUri not found in response.")
        else:
            status_url = response_data['statusQueryGetUri']
            st.write(f"Durable Function started. Polling status at {status_url}")

            with st.spinner("Waiting for function to complete..."):
                while True:
                    status_response = requests.get(status_url)
                    status = status_response.json()

                    if status.get("runtimeStatus") in ["Completed", "Failed", "Terminated"]:
                        st.write(f"Durable Function completed with status: {status['runtimeStatus']}")
                        if "output" in status:
                            st.write(f"Answer: {status['output']['answer']}")
                            st.write(f"Context: {status['output']['context']}")
                            st.session_state.chat_history.append( {"inputs": {"question": input_question}, "outputs": { "answer": status['output']['answer']}})
                        else:
                            st.write("No output returned by the function.")
                        break
                    
                    time.sleep(2)
                    st.write("Still running... Polling again...")
    except requests.exceptions.RequestException as e:
        st.error(f"Error during HTTP request: {e}") 
        

