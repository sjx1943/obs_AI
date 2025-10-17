import os
import re
from typing import List
import json

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("警告：pdfplumber未安装，无法解析PDF文件")

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("警告：python-docx未安装，无法解析Word文件")

try:
    import pandas as pd
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
    print("警告：pandas未安装，无法解析Excel文件")

def read_pdf(path: str) -> str:
    """解析PDF文件"""
    if not PDF_AVAILABLE:
        raise ImportError("请先安装pdfplumber: pip install pdfplumber")
    
    text = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
    except Exception as e:
        raise Exception(f"PDF解析失败: {str(e)}")
    
    return "\n".join(text)

def read_docx(path: str) -> str:
    """解析Word文件"""
    if not DOCX_AVAILABLE:
        raise ImportError("请先安装python-docx: pip install python-docx")
    
    try:
        doc = docx.Document(path)
        text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text)
        return "\n".join(text)
    except Exception as e:
        raise Exception(f"Word文档解析失败: {str(e)}")

def read_excel(path: str) -> str:
    """解析Excel文件"""
    if not EXCEL_AVAILABLE:
        raise ImportError("请先安装pandas和openpyxl: pip install pandas openpyxl")
    
    try:
        # 读取所有sheet
        excel_file = pd.ExcelFile(path)
        all_text = []
        
        for sheet_name in excel_file.sheet_names:
            df = excel_file.parse(sheet_name)
            # 填充空值
            df = df.fillna("")
            
            # 将DataFrame转换为文本
            sheet_text = f"\n=== {sheet_name} ===\n"
            sheet_text += df.to_string(index=False)
            all_text.append(sheet_text)
        
        return "\n\n".join(all_text)
    except Exception as e:
        raise Exception(f"Excel文件解析失败: {str(e)}")

def read_txt(path: str) -> str:
    """解析文本文件"""
    try:
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
        text = None
        
        for encoding in encodings:
            try:
                with open(path, "r", encoding=encoding) as f:
                    text = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        if text is None:
            raise Exception("无法解码文件，请检查文件编码")
        
        return text
    except Exception as e:
        raise Exception(f"文本文件解析失败: {str(e)}")

def read_json(path: str) -> str:
    """解析JSON文件"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        raise Exception(f"JSON文件解析失败: {str(e)}")

def read_any(path: str) -> str:
    """根据文件扩展名选择解析方法"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"文件不存在: {path}")
    
    ext = os.path.splitext(path)[1].lower()
    
    parser_map = {
        '.pdf': read_pdf,
        '.docx': read_docx,
        '.doc': read_docx,
        '.xlsx': read_excel,
        '.xls': read_excel,
        '.txt': read_txt,
        '.md': read_txt,
        '.csv': read_txt,
        '.json': read_json
    }
    
    parser = parser_map.get(ext)
    if parser:
        return parser(path)
    else:
        # 尝试作为文本文件读取
        return read_txt(path)

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """将文本分割为块"""
    # 清理文本
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    
    if len(text) <= chunk_size:
        return [text] if text else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        # 尝试在句号或段落边界处断开
        if end < len(text):
            # 寻找最近的句号或换行
            for boundary in ['\n\n', '\n', '。', '？', '！', '.', '?', '!']:
                boundary_pos = text.rfind(boundary, start, end)
                if boundary_pos > start:
                    end = boundary_pos + len(boundary)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # 计算下一个开始位置
        start = max(end - overlap, start + 1)
        if start >= len(text):
            break
    
    return chunks

def get_supported_extensions() -> List[str]:
    """获取支持的文件扩展名列表"""
    extensions = ['.txt', '.md', '.csv', '.json']
    
    if PDF_AVAILABLE:
        extensions.append('.pdf')
    if DOCX_AVAILABLE:
        extensions.extend(['.docx', '.doc'])
    if EXCEL_AVAILABLE:
        extensions.extend(['.xlsx', '.xls'])
    
    return extensions