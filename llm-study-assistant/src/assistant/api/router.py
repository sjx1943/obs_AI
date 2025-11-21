import os
import shutil
import uuid
from typing import List
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

# Import from the new structured packages
from ..services.rag import RAGPipeline
from ..services.obs import OBSController
from ..services.parsers import get_supported_extensions
from .schemas import (
    UploadResp, AskRequest, AskResponse, SourceChunk,
    RecordingRequest, RecordingResponse, OBSConnectionStatus
)
from ..services.video_processing import extract_text_from_video, parse_ocr_text_to_qa

# --- Router and Dependencies Setup ---

router = APIRouter()

# In a real-world scenario, these would be managed by a dependency injection system.
# For simplicity, we'll instantiate them here. A more robust solution would be
# to use FastAPI's `Depends` feature.
rag_pipeline = RAGPipeline()
obs_controller = OBSController()

# Use absolute paths based on the project root for stability
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.getenv("DATA_DIR", os.path.join(PROJECT_ROOT, "data"))
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
RECORDING_DIR = os.getenv("RECORDING_OUTPUT_DIR", os.path.join(DATA_DIR, "recordings"))

# 确保所有必需的目录都存在
for directory in [DATA_DIR, UPLOAD_DIR, RECORDING_DIR]:
    os.makedirs(directory, exist_ok=True)

# ============ System & Health Routes ============

@router.get("/health")
def health():
    return {
        "ok": True,
        "timestamp": datetime.now().isoformat(),
        "status": rag_pipeline.get_status()
    }

@router.get("/system/status")
def system_status():
    return {
        "rag_status": rag_pipeline.get_status(),
        "obs_status": obs_controller.get_connection_status().dict(),
        "supported_extensions": get_supported_extensions(),
        "directories": {
            "data": DATA_DIR,
            "uploads": UPLOAD_DIR,
            "recordings": RECORDING_DIR
        }
    }

# ============ Document Upload & Management Routes ============

@router.post("/upload", response_model=UploadResp)
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload documents and add them to the knowledge base."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    # This logic is now delegated to the RAG service/pipeline
    try:
        result = rag_pipeline.add_files(files, UPLOAD_DIR)
        return UploadResp(
            ok=len(result["saved_files"]) > 0,
            files=result["saved_files"],
            added_chunks=result["added_chunks"],
            message=result["message"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

@router.get("/knowledge/stats")
def get_knowledge_stats():
    """Get knowledge base statistics."""
    return rag_pipeline.get_knowledge_stats()

# ============ RAG QA Routes ============

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """Ask a question to the RAG pipeline."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    result = rag_pipeline.solve(
        qtype=request.type,
        question=request.question,
        options=request.options,
        top_k=request.top_k
    )

    return AskResponse(
        raw=result["raw"],
        contexts=[SourceChunk(**ctx) for ctx in result["contexts"]],
        timestamp=datetime.now()
    )

# ============ OBS Recording Routes ============

@router.get("/obs/status", response_model=OBSConnectionStatus)
def get_obs_status():
    """Get OBS connection status."""
    return obs_controller.get_connection_status()

@router.post("/obs/connect")
def connect_obs():
    """Connect to OBS Studio."""
    success = obs_controller.connect()
    return {
        "success": success,
        "message": "Connection successful" if success else "Connection failed",
        "status": obs_controller.get_connection_status().dict()
    }

@router.post("/obs/disconnect")
def disconnect_obs():
    """Disconnect from OBS Studio."""
    obs_controller.disconnect()
    return {
        "success": True,
        "message": "Disconnected",
        "status": obs_controller.get_connection_status().dict()
    }

@router.post("/obs/recording", response_model=RecordingResponse)
def control_recording(request: RecordingRequest):
    """Control OBS recording (start, stop, pause, resume)."""
    action_map = {
        "start": obs_controller.start_recording,
        "stop": obs_controller.stop_recording,
        "pause": obs_controller.pause_recording,
        "resume": obs_controller.resume_recording,
    }
    if request.action not in action_map:
        raise HTTPException(status_code=400, detail=f"Unsupported action: {request.action}")

    if request.action == "start":
        response = action_map[request.action](request.output_path)
    else:
        response = action_map[request.action]()
        
    return response

@router.get("/obs/recording/status")
def get_recording_status():
    return obs_controller.get_recording_status()

# ============ Recording File Management Routes ============

@router.get("/recordings")
def list_recordings():
    """List available recording files."""
    return {
        "files": obs_controller.get_recording_files(),
        "directory": RECORDING_DIR
    }

@router.get("/recordings/{filename}")
def download_recording(filename: str):
    """Download a recording file."""
    file_path = os.path.join(RECORDING_DIR, filename)
    if not os.path.exists(file_path) or not os.path.abspath(file_path).startswith(os.path.abspath(RECORDING_DIR)):
        raise HTTPException(status_code=404, detail="File not found or access denied")
    return FileResponse(file_path, filename=filename)

@router.delete("/recordings/{filename}")
def delete_recording(filename: str):
    """Delete a recording file."""
    file_path = os.path.join(RECORDING_DIR, filename)
    if not os.path.exists(file_path) or not os.path.abspath(file_path).startswith(os.path.abspath(RECORDING_DIR)):
        raise HTTPException(status_code=404, detail="File not found or access denied")
    try:
        os.remove(file_path)
        return {"success": True, "message": f"Deleted file: {filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.post("/recordings/{filename}/analyze", response_model=AskResponse)
async def analyze_recording(filename: str):
    """Analyze a recording to extract Q&A and find answers."""
    file_path = os.path.join(RECORDING_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # This complex logic should be in the service layer
        analysis_result = rag_pipeline.analyze_video(file_path)
        
        if analysis_result["status"] == "failed":
            raise HTTPException(status_code=400, detail=analysis_result["message"])

        return AskResponse(
            raw={"video_analysis_results": analysis_result["raw_answers"]},
            contexts=analysis_result["all_contexts"],
            timestamp=datetime.now()
        )
    except Exception as e:
        import traceback
        print(f"Video analysis error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Video analysis failed: {str(e)}")