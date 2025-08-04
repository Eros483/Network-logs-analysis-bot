# backend/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile
import os
import sys
from typing import Dict, Any

# Add the parent directory to the Python path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logs_analysis import DocumentAnalysis
from src.chatbot import ChatBot
from prompt_templates.templates import default_chat_template

app = FastAPI(title="Network Logs Analysis API", version="1.0.0")

# Add CORS middleware to allow requests from Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to store analysis results and chatbot
analysis_results = {}
chatbot_instance = None

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/")
async def root():
    return {"message": "Network Logs Analysis API is running"}

@app.post("/upload-logs")
async def upload_logs(file: UploadFile = File(...)):
    """
    Upload and analyze network logs
    """
    global analysis_results, chatbot_instance
    
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")
    
    try:
        # Create a temporary file to store the uploaded content
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as temp_file:
            content = await file.read()
            temp_file.write(content.decode('utf-8'))
            temp_file_path = temp_file.name
        
        # Analyze the logs
        doc_analysis = DocumentAnalysis(temp_file_path)
        results = doc_analysis.run()
        
        # Store results globally
        analysis_results = results
        
        # Initialize chatbot with the analysis
        system_prompt = default_chat_template(results["logs_analysis"])
        chatbot_instance = ChatBot(system_prompt=system_prompt)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return {
            "message": "File uploaded and analyzed successfully",
            "filename": file.filename,
            "analysis_available": True
        }
        
    except Exception as e:
        # Clean up temporary file in case of error
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/logs-analysis")
async def get_logs_analysis():
    """
    Get the network logs analysis results
    """
    if not analysis_results:
        raise HTTPException(status_code=404, detail="No analysis results available. Please upload logs first.")
    
    return {
        "logs_analysis": analysis_results.get("logs_analysis", ""),
        "has_data": True
    }

@app.get("/anomalies")
async def get_anomalies():
    """
    Get the identified anomalies and recommended actions
    """
    if not analysis_results:
        raise HTTPException(status_code=404, detail="No analysis results available. Please upload logs first.")
    
    return {
        "anomalies": analysis_results.get("anomalies", ""),
        "has_data": True
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    """
    Chat with the network logs analysis bot
    """
    global chatbot_instance
    
    if not chatbot_instance:
        raise HTTPException(status_code=400, detail="Chatbot not initialized. Please upload logs first.")
    
    try:
        response = chatbot_instance.chat(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.post("/clear-chat")
async def clear_chat():
    """
    Clear the chat conversation history
    """
    global chatbot_instance
    
    if not chatbot_instance:
        raise HTTPException(status_code=400, detail="Chatbot not initialized. Please upload logs first.")
    
    try:
        chatbot_instance.clear_conversation()
        return {"message": "Chat history cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear chat: {str(e)}")

@app.get("/status")
async def get_status():
    """
    Get the current status of the application
    """
    return {
        "analysis_available": bool(analysis_results),
        "chatbot_initialized": chatbot_instance is not None,
        "ollama_model": "llama3.1:8b-instruct-q4_K_M"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)