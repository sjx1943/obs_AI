from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any, Union
from datetime import datetime

class UploadedFileInfo(BaseModel):
    filename: str
    doc_id: str
    chunks: int

class UploadResp(BaseModel):
    ok: bool
    files: List[UploadedFileInfo]
    added_chunks: int
    message: str = ""

QuestionType = Literal["single_choice","multi_choice","true_false","subjective","auto"]

class AskRequest(BaseModel):
    type: QuestionType = "auto"
    question: str
    options: Optional[List[str]] = None
    top_k: int = 5
    context: Optional[str] = None

class SourceChunk(BaseModel):
    doc_id: str
    chunk_id: int
    text: str
    score: float = 0.0

class AskResponse(BaseModel):
    raw: Any
    contexts: List[SourceChunk]
    timestamp: datetime = Field(default_factory=datetime.now)

# OBS相关模型
class RecordingStatus(BaseModel):
    is_recording: bool
    output_active: bool = False
    output_paused: bool = False
    output_duration: Optional[float] = None
    current_program_scene: Optional[str] = None

class RecordingRequest(BaseModel):
    action: Literal["start", "stop", "pause", "resume"]
    scene_name: Optional[str] = None
    output_path: Optional[str] = None

class RecordingResponse(BaseModel):
    success: bool
    message: str
    status: Optional[RecordingStatus] = None
    file_path: Optional[str] = None

class OBSConnectionStatus(BaseModel):
    connected: bool
    host: Optional[str] = None
    port: Optional[int] = None
    error: Optional[str] = None

class SystemStatus(BaseModel):
    rag_status: dict
    obs_status: OBSConnectionStatus
    supported_extensions: List[str]
    directories: dict
