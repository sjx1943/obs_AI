import os
import shutil
import uuid
from typing import List, Dict, Any

from fastapi import UploadFile

from .store import VectorStore
from .llm import LLMClient
from .prompts import (
    SYSTEM_PROMPT, CLASSIFIER_PROMPT, VIDEO_CLASSIFIER_PROMPT, SOLVER_PREFIX,
    SOLVER_SINGLE, SOLVER_MULTI, SOLVER_TF, SOLVER_SUBJ,
    check_compliance, get_compliance_response
)
from .parsers import read_any, chunk_text
from .video_processing import extract_text_from_video, parse_ocr_text_to_qa

def make_sources(objs: List[Dict]) -> str:
    """Formats retrieved chunks into a context string for the model."""
    if not objs:
        return "No relevant documents found."
    lines = []
    for d in objs:
        text_preview = d['text'].replace('\n', ' ')[:200]
        line = f"[{d['doc_id']}#{d['chunk_id']}] (Score: {d.get('score', 0.0):.2f}) {text_preview}..."
        lines.append(line)
    return "\n".join(lines)

class RAGPipeline:
    """Handles the entire RAG process from document ingestion to question answering."""

    def __init__(self):
        data_dir = os.getenv("DATA_DIR", "./data")
        self.store = VectorStore(data_dir)
        self.llm = LLMClient()

    def get_status(self) -> Dict[str, Any]:
        """Gets the status of the RAG components."""
        # Actively test the connection before getting info
        self.llm.test_connection(max_retries=1)
        
        llm_info = self.llm.get_model_info()
        store_stats = self.store.get_stats()
        return {
            "llm_available": llm_info["available"],
            "llm_model": llm_info["model"],
            "embedding_available": store_stats["embedding_available"],
            "embedding_model": os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5"),
            "index_available": store_stats["index_vectors"] > 0,
        }

    def add_files(self, files: List[UploadFile], upload_dir: str) -> Dict[str, Any]:
        """Processes uploaded files and adds them to the vector store."""
        added_chunks = 0
        saved_files = []
        errors = []

        for file in files:
            if not file.filename:
                continue
            try:
                ext = os.path.splitext(file.filename)[1].lower()
                doc_id = f"{uuid.uuid4().hex}{ext}"
                dst_path = os.path.join(upload_dir, doc_id)

                with open(dst_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)

                text_content = read_any(dst_path)
                if not text_content.strip():
                    errors.append(f"{file.filename}: File is empty")
                    continue

                chunk_size = int(os.getenv("CHUNK_SIZE", "500"))
                overlap = int(os.getenv("CHUNK_OVERLAP", "100"))
                chunks = chunk_text(text_content, chunk_size=chunk_size, overlap=overlap)

                if not chunks:
                    errors.append(f"{file.filename}: Could not chunk document")
                    continue

                added = self.store.add(doc_id, chunks)
                added_chunks += added
                saved_files.append({"filename": file.filename, "doc_id": doc_id, "chunks": added})

            except Exception as e:
                errors.append(f"{file.filename}: {str(e)}")

        message = f"Successfully processed {len(saved_files)} files, adding {added_chunks} chunks."
        if errors:
            message += f"\nErrors: {'; '.join(errors)}"

        return {
            "saved_files": saved_files,
            "added_chunks": added_chunks,
            "message": message
        }

    def classify(self, question: str, options: List[str] = None, is_video_content: bool = False) -> str:
        """Classifies the question type."""
        if check_compliance(question):
            return "compliance_check"

        prompt_template = VIDEO_CLASSIFIER_PROMPT if is_video_content else CLASSIFIER_PROMPT
        user_content = f"Question: {question}\nOptions: {options or 'None'}"
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{prompt_template}\n\n{user_content}"}
        ]
        response = self.llm.chat(messages, max_tokens=200, json_mode=True)

        if isinstance(response, dict) and response.get("type") in {"single_choice", "multi_choice", "true_false", "subjective"}:
            return response["type"]
        return "subjective"

    def solve(self, qtype: str, question: str, options: List[str] = None, top_k: int = 5) -> Dict:
        """Solves a question using the RAG pipeline."""
        if qtype == "compliance_check" or check_compliance(question):
            return {"raw": get_compliance_response(), "contexts": []}

        contexts = self.store.search(question, top_k=top_k)
        contexts_text = make_sources(contexts)

        type_prompts = {
            "single_choice": SOLVER_SINGLE,
            "multi_choice": SOLVER_MULTI,
            "true_false": SOLVER_TF,
            "subjective": SOLVER_SUBJ,
        }
        solver_prompt = type_prompts.get(qtype, SOLVER_SUBJ)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{SOLVER_PREFIX}\n\nContexts:\n{contexts_text}\n\nQuestion:\n{question}\n\nOptions:\n{options or 'None'}\n\n{solver_prompt}"}
        ]
        result = self.llm.chat(messages, max_tokens=800, json_mode=True)

        if not isinstance(result, dict) or "error" in result:
            result = {
                "final_answer": "Failed to parse LLM response.",
                "confidence": 0.1,
                "brief_rationale": f"LLM output format error: {result.get('raw_content', '')[:100]}",
            }

        return {"raw": result, "contexts": contexts}

    def analyze_video(self, video_path: str) -> Dict[str, Any]:
        """Analyzes a video, extracts Q&A, and solves them."""
        extracted_text = extract_text_from_video(video_path)
        if not extracted_text.strip():
            return {"status": "failed", "message": "No text extracted from video", "results": []}

        qa_pairs = parse_ocr_text_to_qa(extracted_text)
        if not qa_pairs:
            qa_pairs = [{"question": extracted_text.strip(), "options": None}]

        analysis_results = []
        for qa in qa_pairs:
            qtype = self.classify(qa["question"], qa.get("options"), is_video_content=True)
            result = self.solve(qtype=qtype, question=qa["question"], options=qa.get("options"), top_k=5)
            analysis_results.append({
                "question": qa["question"],
                "options": qa.get("options"),
                "answer": result
            })
        
        # Reformat for API response
        all_contexts = []
        raw_answers = []
        for res in analysis_results:
            answer_data = res["answer"]
            raw_answers.append({
                "question": res["question"],
                "options": res["options"],
                "answer": answer_data["raw"]
            })
            all_contexts.extend(answer_data["contexts"])

        return {
            "status": "completed",
            "message": "Analysis successful",
            "raw_answers": raw_answers,
            "all_contexts": all_contexts
        }

    def get_knowledge_stats(self) -> Dict:
        """Gets knowledge base statistics."""
        return self.store.get_stats()