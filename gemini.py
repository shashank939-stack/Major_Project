import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import win32com.client
import os
import speech_recognition as sr

from PIL import Image
speaker=win32com.client.Dispatch("SAPI.SpVoice")
load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
def recognize_speech_from_mic():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        st.write("Listening...")
        audio = r.listen(source)
        try:
            query = r.recognize_google(audio, language="en-IN")
            st.write(f"User Said: {query}")
            return query
        except sr.UnknownValueError:
            st.write("Google Speech Recognition could not understand audio")
            return ""
        except sr.RequestError as e:
            st.write(f"Could not request results from Google Speech Recognition service; {e}")
            return ""
            
def get_pdf_text(pdf_docs):
    text=""
    for pdf in pdf_docs:
        pdf_reader= PdfReader(pdf)
        for page in pdf_reader.pages:
            text+= page.extract_text()
    return  text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context in human like english language And it should seem like human is giving the answer in formal language, make sure to provide all the details, and if user says hey or hello then only answer Hey then say name if provided and greet and ask him " I am your assistant feel free to ask your query. I would Like to resolve your query". if user says any negative query tell him to maintain decorem and threat him to do not repeat mistake.Try to answer all the related questions if question is about the given data then try to answer .if any decision making question then answer based upon the data provided .if the answer is not in
    provided context just say, "Sorry Sir/Ma'am  I am not able to answer your query please ask another.", don't provide the wrong answer\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Set allow_dangerous_deserialization to True
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()
    response = chain(
        {"input_documents": docs, "question": user_question},
        return_only_outputs=True
    )
    print(response)
    st.write("Reply: ", response["output_text"])
    speaker.speak(response["output_text"])
    


def main():
    st.set_page_config("InfoCallHub")
    st.header("Info Call Hub💁")
    st.markdown("<h4>🎙️ Interactive Call System:</h4>", unsafe_allow_html=True)
    if st.button("🎧 Start Listening"):
        st.write("Click the button and start speaking...")
        query = recognize_speech_from_mic()
        user_question = query
        speaker.speak(user_question)
        if user_question:
             user_input(user_question)

    

    with st.sidebar:
        st.markdown("<h4>📄 Upload Company-Related PDF File:</h4>", unsafe_allow_html=True)
        pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True, help="Upload a single PDF file related to the company")
        # pdf_docs="infosys.pdf"
        if st.button("🚀 Submit & Process", help="Click to process the PDF and start the call"):
            with st.spinner("Processing..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)
                st.success("Done")
                st.balloons() 
                


if __name__ == "__main__":
    main()

