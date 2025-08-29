from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from src.gradient_editor import GradientEditorCrew

load_dotenv()

app = FastAPI(
    title="AI Gradient Editor API",
    description="API for generating SVG gradients from natural language using CrewAI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GradientRequest(BaseModel):
    instruction: str
    svg_content: Optional[str] = ""
    api_key: Optional[str] = None

class GradientResponse(BaseModel):
    success: bool
    svg_output: str
    message: str
    process_details: Optional[dict] = None

@app.get("/")
async def root():
    return {"message": "AI Gradient Editor API", "version": "1.0.0"}

@app.post("/generate-gradient", response_model=GradientResponse)
async def generate_gradient(request: GradientRequest):
    """Generate SVG gradient from natural language instruction"""
    
    try:
        if request.api_key:
            os.environ["OPENAI_API_KEY"] = request.api_key

        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=400, 
                detail="OpenAI API key is required. Provide it in the request or set OPENAI_API_KEY environment variable."
            )
        
        crew = GradientEditorCrew()
        

        result = crew.generate_gradient(request.instruction, request.svg_content)
        
        if result['success']:
            return GradientResponse(
                success=True,
                svg_output=result['svg_output'],
                message="Gradient generated successfully",
                process_details=result.get('result', {})
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to generate gradient")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating gradient: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Gradient Editor"}

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", 8000))
    
    uvicorn.run(app, host=host, port=port)
