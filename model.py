import streamlit as st
import replicate
import os


B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"

def get_prompt( new_system_prompt ):
    SYSTEM_PROMPT = B_SYS + new_system_prompt + E_SYS
    prompt_template =  B_INST + SYSTEM_PROMPT + E_INST
    return prompt_template

def cut_off_text(text, prompt):
    cutoff_phrase = prompt
    index = text.find(cutoff_phrase)
    if index != -1:
        return text[:index]
    else:
        return text

def remove_substring(string, substring):
    return string.replace(substring, "")



# Step 2: Add a title to your Streamlit Application on Browser

st.set_page_config(page_title="💬 AutismCare Companion Chatbot with Streamlit")


#Create a Side bar
with st.sidebar:
    st.title("💬 AutismCare Companion Chatbot")
    st.header("Settings")

    if 'REPLICATE_API_TOKEN' in st.secrets:
        st.success('API key already provided!', icon='✅')
        add_replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        add_replicate_api=st.text_input('Enter the API token', type='password')
        if not (add_replicate_api.startswith('r8_') and len(add_replicate_api)==40):
            st.warning('Please enter your credentials', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')

    st.subheader("Kindly click the provided link to complete the form and obtain your API token for running the chatbot [link](https://docs.google.com/forms/d/e/1FAIpQLSdqAiXYk1Wk36Ocjpi6bdZo3GFALkqWh5PwwSzSmisFLp3wnw/viewform)")


    llm = 'lucataco/llama-2-7b-chat:6ab580ab4eef2c2b440f2441ec0fc0ace5470edaf2cbea50b8550aec0b3fbd38'

    #st.markdown('Buy me a coffee [link](https://www.buymeacoffee.com/ishubham4)')
    os.environ['REPLICATE_API_TOKEN']=add_replicate_api

#Store the LLM Generated Reponese

if "messages" not in st.session_state.keys():
    st.session_state.messages=[{"role": "assistant", "content":"How may I assist you today?"}]

# Diplay the chat messages

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Clear the Chat Messages
def clear_chat_history():
    st.session_state.messages=[{"role":"assistant", "content": "How may I assist you today"}]

st.sidebar.button('Clear Chat History', on_click=clear_chat_history)



# Create a Function to generate the Llama 2 Response
def generate_llama2_response(prompt_input):
    default_system_prompt="""\
    You are a helpful, child psychiatrist assistant at "Child Development & Treatment Centre" and honest. Always answer as helpfully as possible, while being safe and then you stop. The answer should be short, straight and to the point. If you don't know the answer to a question, please don't share false information."""

    new_prompt = get_prompt(default_system_prompt)
    for data in st.session_state.messages:
        print("Data:", data)
        if data["role"]=="user":
            new_prompt+="User: " + data["content"] + "\n\n"
        else:
            new_prompt+="Assistant" + data["content"] + "\n\n"
    output = replicate.run(llm, input={"prompt": f"{new_prompt} {prompt_input} Assistant: ",
                                     "temperature":0.1})
    final_outputs = cut_off_text(output, '</s>')
    final_outputs = remove_substring(final_outputs, new_prompt)


    return final_outputs


#User -Provided Prompt

if prompt := st.chat_input(disabled=not add_replicate_api):
    st.session_state.messages.append({"role": "user", "content":prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a New Response if the last message is not from the asssistant

if st.session_state.messages[-1]["role"] != "assistant":
    with st.spinner("Patience..."):
        response = generate_llama2_response(prompt)
        response_text = "".join(response)  # Convert the list of responses to a single string

        # Extract the relevant message
        start_index = response_text.find("Assistant: [/INST]")
        if start_index != -1:
            relevant_message = response_text[start_index + len("Assistant: [/INST]"):]
            st.write(relevant_message)
            message = {"role": "assistant", "content": relevant_message}
            st.session_state.messages.append(message)




