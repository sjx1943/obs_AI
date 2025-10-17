import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    import obsws_python as obs
    OBS_AVAILABLE = True
except ImportError:
    obs = None
    OBS_AVAILABLE = False

from ..api.schemas import RecordingStatus, RecordingResponse, OBSConnectionStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OBSController:
    def __init__(self):
        self.host = os.getenv("OBS_HOST", "localhost")
        self.port = int(os.getenv("OBS_PORT", 4455))
        self.password = os.getenv("OBS_PASSWORD", "")
        self.recording_dir = os.getenv("RECORDING_OUTPUT_DIR", "./data/recordings")
        self.recording_format = os.getenv("RECORDING_FORMAT", "mp4")
        os.makedirs(self.recording_dir, exist_ok=True)
        self.client = None
        self.connected = False

    def connect(self) -> bool:
        """连接到OBS Studio"""
        if not OBS_AVAILABLE:
            return False
        try:
            self.client = obs.ReqClient(host=self.host, port=self.port, password=self.password)
            version_info = self.client.get_version()
            self.connected = True
            logger.info(f"成功连接到OBS Studio: {version_info.obs_version}")
            return True
        except Exception as e:
            self.connected = False
            logger.error(f"OBS连接失败: {str(e)}")
            return False

    def disconnect(self):
        """断开OBS连接"""
        if self.client:
            try:
                self.client.disconnect()
                self.connected = False
                logger.info("已断开OBS连接")
            except Exception as e:
                logger.error(f"断开OBS连接时错误: {str(e)}")

    def get_connection_status(self) -> OBSConnectionStatus:
        """检查与OBS WebSocket的连接状态"""
        if not OBS_AVAILABLE:
            logger.warning("OBS功能不可用，因为 'obsws-python' 未安装。")
            return OBSConnectionStatus(connected=False, error="obsws-python is not installed")

        logger.info(f"正在检查OBS连接 -> ws://{self.host}:{self.port}")
        try:
            # 使用一个新的临时客户端实例来检查连接，避免干扰主客户端
            client = obs.ReqClient(host=self.host, port=self.port, password=self.password, timeout=3)
            version = client.get_version()
            logger.info(f"✓ OBS连接成功 (OBS Studio v{version.obs_version}, WebSocket v{version.obs_web_socket_version})")
            return OBSConnectionStatus(connected=True)
        except Exception as e:
            error_message = f"{e.__class__.__name__}: {e}"
            logger.error(f"✗ OBS连接失败: {error_message}")
            logger.error("请确保OBS Studio正在运行，并且WebSocket服务器已在“工具”->“WebSocket服务器设置”中启用。")
            logger.error(f"同时检查.env文件中的OBS_HOST, OBS_PORT, 和 OBS_PASSWORD配置是否正确。")
            return OBSConnectionStatus(connected=False, error=error_message)

    def get_recording_status(self) -> RecordingStatus:
        """获取录屏状态，增加健壮性检查"""
        default_status = RecordingStatus(is_recording=False, output_active=False)
        
        if not self.connected or not self.client:
            return default_status
        
        try:
            # 调用API
            record_status_response = self.client.get_record_status()

            # 关键：检查返回的对象是否是期望的类型
            # obsws_python 在成功时返回一个 <class 'obsws_python.classes.RecordStatus'> 对象
            if not isinstance(record_status_response, responses.RecordStatus):
                print(f"获取录屏状态失败：返回了非预期的对象类型 {type(record_status_response)}")
                return default_status

            # 获取当前场景名称
            try:
                current_scene_response = self.client.get_current_program_scene()
                scene_name = current_scene_response.current_program_scene_name
            except Exception:
                scene_name = "未知" # 如果获取场景失败，则提供一个默认值

            return RecordingStatus(
                is_recording=record_status_response.output_active,
                output_active=record_status_response.output_active,
                output_paused=record_status_response.output_paused,
                output_duration=record_status_response.output_duration,
                current_program_scene=scene_name
            )
        except Exception as e:
            print(f"获取录屏状态时发生异常: {str(e)}")
            # 发生任何异常（如连接断开），都返回安全的离线状态
            self.connected = False # 标记为断开连接
            return default_status

    def start_recording(self, output_path: Optional[str] = None) -> RecordingResponse:
        """开始录屏"""
        if not self.connected and not self.connect():
            return RecordingResponse(success=False, message="无法连接到OBS Studio")
        try:
            status = self.get_recording_status()
            if status.is_recording:
                return RecordingResponse(success=False, message="已在录屏中", status=status)
            if output_path:
                self.client.set_record_directory(output_path)
            self.client.start_record()
            new_status = self.get_recording_status()
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"recording_{timestamp}.{self.recording_format}"
                full_path = os.path.join(self.recording_dir, filename)
            else:
                full_path = output_path
            return RecordingResponse(success=True, message="开始录屏成功", status=new_status, file_path=full_path)
        except Exception as e:
            return RecordingResponse(success=False, message=f"开始录屏失败: {str(e)}")

    def stop_recording(self) -> RecordingResponse:
        """停止录屏"""
        if not self.connected:
            return RecordingResponse(success=False, message="未连接到OBS Studio")
        try:
            status = self.get_recording_status()
            if not status.is_recording:
                return RecordingResponse(success=False, message="当前未在录屏", status=status)
            self.client.stop_record()
            new_status = self.get_recording_status()
            return RecordingResponse(success=True, message="停止录屏成功", status=new_status)
        except Exception as e:
            return RecordingResponse(success=False, message=f"停止录屏失败: {str(e)}")

    def pause_recording(self) -> RecordingResponse:
        """暂停录屏"""
        if not self.connected:
            return RecordingResponse(success=False, message="未连接到OBS Studio")
        try:
            self.client.pause_record()
            status = self.get_recording_status()
            return RecordingResponse(success=True, message="暂停录屏成功", status=status)
        except Exception as e:
            return RecordingResponse(success=False, message=f"暂停录屏失败: {str(e)}")

    def resume_recording(self) -> RecordingResponse:
        """恢复录屏"""
        if not self.connected:
            return RecordingResponse(success=False, message="未连接到OBS Studio")
        try:
            self.client.resume_record()
            status = self.get_recording_status()
            return RecordingResponse(success=True, message="恢复录屏成功", status=status)
        except Exception as e:
            return RecordingResponse(success=False, message=f"恢复录屏失败: {str(e)}")

    def switch_scene(self, scene_name: str) -> Dict[str, Any]:
        """切换场景"""
        if not self.connected:
            return {"error": "未连接到OBS Studio"}
        try:
            self.client.set_current_program_scene(scene_name)
            return {"success": True, "message": f"切换到场景: {scene_name}"}
        except Exception as e:
            return {"error": f"切换场景失败: {str(e)}"}

    def get_recording_files(self) -> List[Dict[str, Any]]:
        """获取录屏文件列表"""
        files = []
        if not os.path.exists(self.recording_dir):
            return files
        for filename in os.listdir(self.recording_dir):
            file_path = os.path.join(self.recording_dir, filename)
            if os.path.isfile(file_path) and filename.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "path": file_path,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        files.sort(key=lambda x: x["created"], reverse=True)
        return files