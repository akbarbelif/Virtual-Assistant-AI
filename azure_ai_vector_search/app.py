from backend.biz_azure_ai_search import *
from azure_open_ai.azure_open_ai import *
from azure_open_ai.langchain_azure_openai import *
from streamlit_chat import message
from PIL import Image
import streamlit as st
import random
import time

company = "UPM"
# Page icon
icon = Image.open(f'azure_ai_vector_search/src/{company}_Logo.png')

st.set_page_config(page_title=f"{company} Virtual Assistant Using AI Search Engine", page_icon=icon, layout="wide", initial_sidebar_state="collapsed", menu_items=None)
# openai.api_key = st.secrets.openai_credentials.openai_key
st.title(f"{company} Virtual Assistant Using AI Search Engine 💬")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Create placeholders for chat messages
message_placeholders = {}

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    message_placeholders[role] = st.empty()
    with st.chat_message(role):
        st.markdown(content)

st.sidebar.markdown("## Search Engine")
selected_analysis = st.sidebar.radio("Select the Analysis Type", \
                                 ('Exhaustive KNN Search',
                                  'Vector Search', 
                                  'Hybrid Search',
                                  'Semantic Search'))
st.sidebar.markdown("<hr/>",unsafe_allow_html=True) 
st.sidebar.subheader("Configuration")  
# use_langchain = st.sidebar.checkbox("Use Langchain", value=True)
use_langchain = True
NUMBER_OF_RESULTS_TO_RETURN = st.sidebar.slider("Number of Search Results to Return",\
                                                 1, 100, 1)
# attachment = st.sidebar.file_uploader("Attach a file (optional)", type=["xlsx"])

# Accept user input and attachment
user_input = st.chat_input("Your question")
attachment = st.sidebar.file_uploader("Attach a file (optional)", type=["xlsx"])

# FUNCTION 
def get_reply(user_input, content):
    conversation=[{"role": "system", "content": "Assistant is a great language model formed by OpenAI."}]
    reply = generate_reply_from_context(user_input, content, conversation)
    return reply

def get_details(results_content, results_source):
    with st.expander("See explanation"):
    # st.write(\"\"\"
    # st.markdown("### Details are:")
        for (result,metadata) in zip(results_content,results_source):
            st.write("<html><b>" + 
                    metadata + "</b></html>",
                    unsafe_allow_html=True)
            st.write(result)
            st.write("----")

def get_search_results_azure_aisearch(selected_analysis, user_input):

    """
    This function returns the results from the Azure AI Search Engine

    Returns:
        [results_content,results_source]: 
        Results content and Results Source is returned
    """
    if selected_analysis == 'Vector Search':
       results_content,results_source = \
       get_results_vector_search(user_input,
        NUMBER_OF_RESULTS_TO_RETURN = NUMBER_OF_RESULTS_TO_RETURN)
    elif selected_analysis == 'Hybrid Search':
         results_content,results_source = \
            get_results_vector_search(user_input,
            NUMBER_OF_RESULTS_TO_RETURN = NUMBER_OF_RESULTS_TO_RETURN,
            hybrid = True,
            exhaustive_knn=False)
    elif selected_analysis == 'Exhaustive KNN Search':
            results_content,results_source = \
                get_results_vector_search(user_input,
                NUMBER_OF_RESULTS_TO_RETURN = NUMBER_OF_RESULTS_TO_RETURN,
                hybrid = False,
                exhaustive_knn=True)
    elif selected_analysis == 'Semantic Search':
            results_content,results_source = \
                get_results_vector_search(user_input,
                NUMBER_OF_RESULTS_TO_RETURN = NUMBER_OF_RESULTS_TO_RETURN,
                hybrid = False,
                exhaustive_knn=False,
                semantic_search=True)
                
    return results_content,results_source

def get_reply_langchain_st(user_input, content):
    if "conversation_buf" not in st.session_state:
        st.session_state["conversation_buf"] = None
       
    result,conversation_buf,number_of_tokens = \
            get_reply_langchain(st.session_state["conversation_buf"],
                                    content,user_input)
    st.session_state["conversation_buf"] = conversation_buf
    
    return result,number_of_tokens

def show_langchain_history(result):
    st.markdown("### History is provided below:")
    st.write(result["history"])

if user_input or attachment:
    result = {}
    # Prompt for user input and save to chat history
    # Add user message to chat history
    if user_input : 
        st.session_state.messages.append({"role": "user", "content": user_input})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(user_input)

        results_content, results_source = get_search_results_azure_aisearch(selected_analysis, user_input)        
        content = "\n".join(results_content)
        result,number_of_tokens = get_reply_langchain_st(user_input, content)

    if attachment:
            # You can process the attachment here or save it as needed
            # For example, you can save it to a temporary folder and store the file path in the chat history
            # attachment_path = f"azure_ai_vector_search/attachments/{attachment.name}"
            attachment_path = f"azure_ai_vector_search/attachments/{company}_incident.xlsx"
            with open(attachment_path, "wb") as f:
                f.write(attachment.read())

            # Add attachment message to chat history
            st.session_state.messages.append({"role": "user", "content": f"Attachment: {attachment.name}"})
            # Display attachment message in chat message container
            with st.chat_message("user"):
                st.markdown(f"Attachment: {attachment.name}")

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        if result:
            assistant_response = result["response"]
            st.write("Number of tokens used:", number_of_tokens)
            ## get the DETAILS [ CONTENT AND SOURCE ] of the reply from the LLM
            get_details(results_content, results_source)
            st.write("----")
        else:
             assistant_response = random.choice(
            [
                "Hello there! How can I assist you today?",
                f"Hi, human! Is there anything I can help you with {company}?",
                "Do you need help?",
            ]
        )
        # Simulate stream of response with milliseconds delay
        with st.spinner("Thinking..."):
            for chunk in assistant_response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})