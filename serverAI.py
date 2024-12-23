from flask import Flask, request, Response
import google.generativeai as genai
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

load_dotenv()

app = Flask(__name__)

# Initialize Gemini model
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")
genai.configure(api_key=api_key)

def get_conversational_chain():
    prompt_template = """
    You are a call assitant your job is to talk like assitant and provide satisfy answer if user asks comman query regarding phone call  Answer the question as detailed as possible from the provided context in human-like English language donot read puncuation marks comma you have to answer like human. If the user says 'hey' or 'hello', respond with a greeting and offer assistance. For negative queries, ask the user to maintain decorum and warn against repeating mistakes. Answer all related questions based on the provided data. If the answer is not in the provided context, say, "Sorry I am not able to answer your query please ask another."
    \nContext:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """
    # prompt_template = """
    # आप एक लड़की कॉल असिस्टेंट हैं, आपका काम सामान्य प्रश्नों के उत्तर हिंदी में देना है। कृपया दिए गए संदर्भ से यथासंभव विस्तृत उत्तर दें। अगर उपयोगकर्ता 'हेलो' या 'नमस्ते' कहते हैं, तो अभिवादन करें और सहायता की पेशकश करें। अगर कोई नकारात्मक प्रश्न पूछा जाता है, तो उपयोगकर्ता से शालीनता बनाए रखने के लिए कहें और गलतियों को दोहराने से बचें। सभी संबंधित प्रश्नों का उत्तर प्रदान किए गए डेटा के आधार पर दें। यदि उत्तर संदर्भ में नहीं है, तो कहें, "मुझे खेद है, मैं आपके प्रश्न का उत्तर नहीं दे पा रहा हूँ, कृपया दूसरा प्रश्न पूछें।"
    # \nसंदर्भ:\n {context}?\n
    # प्रश्न: \n{question}\n

    # उत्तर:
    # """
    

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Load the vector store
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()
    response = chain(
        {"input_documents": docs, "question": user_question},
        return_only_outputs=True
    )
    return response["output_text"]

@app.route('/handle_response', methods=['POST'])
def handle_response():
    print("handle_response route was called")
    speech_result = request.form.get('SpeechResult')
    print(speech_result)

    if speech_result:
        # Send the speech result to the Gemini model for a response
        response_text = user_input(speech_result)
        print(f"Gemini response: {response_text}")

        response_xml = (
            f'<Response>'
            f'<Say>{response_text}</Say>'
            f'<Gather input="speech" action="  https://9792-14-139-60-2.ngrok-free.app/handle_response" method="POST" language="en-IN" timeout="4">'
            f'<Say>Please ask another question or hang up when done.</Say>'
            f'</Gather>'
            f'</Response>'
        )
    else:
        response_xml = '<Response><Say>No input received. The call will continue until you hang up.</Say></Response>'
    
    return Response(response_xml, mimetype='application/xml')

@app.route('/status_callback', methods=['POST'])
def status_callback():
    call_sid = request.form.get('CallSid')
    call_status = request.form.get('CallStatus')
    
    # Log or process the call status
    print(f"Call SID: {call_sid}, Status: {call_status}")
    
    return Response('<Response></Response>', mimetype='application/xml')

if __name__ == '__main__':
    app.run(port=5000)
