import json
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from app.config import settings as env_settings
import logging

logger = logging.getLogger(__name__)

CONFIG_FILE = Path(__file__).parent.parent.parent / "runtime_config.json"


class RuntimeConfigManager:
    """运行时配置管理器，支持动态修改配置并持久化到文件"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._config: Dict[str, Any] = {}
        self._config_lock = threading.Lock()
        self._load_config()

    def _load_config(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                logger.info(f"Runtime config loaded from {CONFIG_FILE}")
            except Exception as e:
                logger.error(f"Failed to load runtime config: {e}")
                self._config = {}
        else:
            self._config = {}
            logger.info("No runtime config file found, using defaults")

    def _save_config(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            logger.info(f"Runtime config saved to {CONFIG_FILE}")
        except Exception as e:
            logger.error(f"Failed to save runtime config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        with self._config_lock:
            return self._config.get(key, default)

    def set(self, key: str, value: Any):
        with self._config_lock:
            self._config[key] = value
        self._save_config()

    def update(self, updates: Dict[str, Any]):
        with self._config_lock:
            self._config.update(updates)
        self._save_config()

    def get_all(self) -> Dict[str, Any]:
        with self._config_lock:
            return dict(self._config)

    def reset(self, key: str):
        with self._config_lock:
            if key in self._config:
                del self._config[key]
        self._save_config()


runtime_config = RuntimeConfigManager()


class ConfigAccessor:
    """配置访问器，提供便捷的方法获取配置值，优先使用运行时配置，否则回退到环境变量"""

    @staticmethod
    def get_llm_api_key() -> str:
        return runtime_config.get("llm_api_key") or env_settings.LLM_API_KEY

    @staticmethod
    def get_llm_api_url() -> str:
        return runtime_config.get("llm_api_url") or env_settings.LLM_API_URL

    @staticmethod
    def get_llm_model_name() -> str:
        return runtime_config.get("llm_model_name") or env_settings.LLM_MODEL_NAME

    @staticmethod
    def get_llm_temperature() -> float:
        val = runtime_config.get("llm_temperature")
        return val if val is not None else 0.7

    @staticmethod
    def get_llm_max_tokens() -> int:
        val = runtime_config.get("llm_max_tokens")
        return val if val is not None else 500

    @staticmethod
    def get_llm_top_p() -> float:
        val = runtime_config.get("llm_top_p")
        return val if val is not None else 0.9

    @staticmethod
    def get_dashscope_api_key() -> str:
        return runtime_config.get("dashscope_api_key") or env_settings.DASHSCOPE_API_KEY

    @staticmethod
    def get_embedding_model() -> str:
        return runtime_config.get("embedding_model") or env_settings.EMBEDDING_MODEL

    @staticmethod
    def get_embedding_dimension() -> int:
        val = runtime_config.get("embedding_dimension")
        return val if val is not None else env_settings.EMBEDDING_DIMENSION

    @staticmethod
    def get_vision_llm_api_key() -> str:
        return runtime_config.get("vision_llm_api_key") or env_settings.VISION_LLM_API_KEY

    @staticmethod
    def get_vision_llm_model() -> str:
        return runtime_config.get("vision_llm_model") or env_settings.VISION_LLM_MODEL

    @staticmethod
    def get_vision_llm_url() -> str:
        return runtime_config.get("vision_llm_url") or env_settings.VISION_LLM_URL

