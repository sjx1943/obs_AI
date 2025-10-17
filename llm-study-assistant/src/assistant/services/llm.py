import os
import json
import re
import time
import logging
from openai import OpenAI
from typing import List, Dict, Any, Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        base = os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1")
        key = os.getenv("OPENAI_API_KEY", "ollama")
        self.model = os.getenv("LLM_MODEL", "llama3.2:1b-instruct-q4_0")
        if not base or not self.model:
            raise RuntimeError("Please set OPENAI_API_BASE and LLM_MODEL in .env")
        
        self.client = OpenAI(base_url=base, api_key=key)
        self.available = False
        
    def test_connection(self, max_retries: int = 1, retry_delay: int = 2) -> bool:
        """测试与本地LLM的连接，并带有重试机制"""
        logger.info(f"开始测试LLM连接，目标模型: {self.model}, Base URL: {self.client.base_url}")
        for attempt in range(max_retries):
            try:
                self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10,
                    timeout=5
                )
                self.available = True
                logger.info("✓ LLM连接成功。")
                return True
            except Exception as e:
                logger.warning(f"LLM连接尝试 {attempt + 1}/{max_retries} 失败: {e.__class__.__name__}: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"将在 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
        
        logger.error("✗ LLM连接测试在多次重试后最终失败。请确认Ollama服务是否已启动并加载了模型。")
        self.available = False
        return False

    def chat(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.2, 
        max_tokens: int = 800,
        json_mode: bool = False,
        max_retries: int = 2
    ) -> Union[str, Dict, None]:
        """与本地LLM对话，支持JSON模式，并增加了健壮的错误处理和重试"""
        
        for attempt in range(max_retries):
            try:
                if not self.available:
                     if not self.test_connection(max_retries=1, retry_delay=1):
                        raise ConnectionError("无法连接到本地LLM服务。")

                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"} if json_mode else None
                )
                content = resp.choices[0].message.content
                
                if not json_mode:
                    return content

                try:
                    cleaned_content = re.sub(r"```(json)?\s*|\s*```", "", content).strip()
                    return json.loads(cleaned_content)
                except json.JSONDecodeError:
                    return {"error": "LLM输出格式错误", "raw_content": content}

            except Exception as e:
                logger.error(f"LLM调用时发生错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                
                error_message = f"LLM调用失败: {e}"
                if json_mode:
                    return {"error": error_message, "raw_content": ""}
                return error_message
        
        final_error = "LLM服务在多次尝试后依然无响应。"
        if json_mode:
            return {"error": final_error, "raw_content": ""}
        return final_error

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "model": self.model,
            "base_url": self.client.base_url,
            "available": self.available
        }