import gradio as gr
import os
import pinecone
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain import OpenAI
from langchain.vectorstores import Pinecone
from dotenv import load_dotenv

load_dotenv()

pinecone_api =  os.environ['PINECONE_API_KEY']
pinecone_env =  os.environ['PINECONE_ENVIRONMENT']
index_name = os.environ['PINECONE_INDEX']
embeddings = OpenAIEmbeddings(openai_api_key=os.environ['OPENAI_API_KEY'])

def conexion_bbdd():
    pinecone.init(
        api_key=pinecone_api,
        environment=pinecone_env
    )

    docsearch = Pinecone.from_existing_index(index_name, embeddings)

    return docsearch

retriever = conexion_bbdd()
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, ai_prefix='AI Assistant', human_prefix='Friend', output_key='answer')
crc = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0,max_tokens=-1), retriever.as_retriever(), memory=memory, return_source_documents=True)

def respond(message, chat_history):    
    bot_message = crc({"question": message})
    chat_history.append((message, bot_message["answer"]))
    return "", chat_history

with gr.Blocks() as iface:    
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.Button("Clear")
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    iface.launch(share=False, server_name='0.0.0.0', server_port=8080)