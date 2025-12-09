import logging
import logging.config
import os
from datetime import datetime
from pathlib import Path
from backend.utils.timezone import ChinaTimeFormatter, get_china_now


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    log_file: str = None,
    enable_console: bool = True,
    enable_file: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
):
    """
    设置日志配置
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: 日志文件目录
        log_file: 日志文件名，默认为 rag_demo_YYYYMMDD.log
        enable_console: 是否启用控制台输出
        enable_file: 是否启用文件输出
        max_bytes: 单个日志文件最大大小
        backup_count: 保留的日志文件数量
    """
    # 只有启用文件日志时才创建目录和文件路径
    if enable_file:
        log_dir_path = Path(log_dir)
        log_dir_path.mkdir(parents=True, exist_ok=True)
        
        # 默认日志文件名
        if log_file is None:
            today = get_china_now().strftime("%Y%m%d")
            log_file = f"rag_demo_{today}.log"
        
        log_file_path = log_dir_path / log_file
    else:
        log_dir_path = None
        log_file_path = None
    
    # 日志格式
    # 配置字典 - 使用root logger统一管理，自动支持所有模块
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": "%(asctime)s - %(levelname)s - %(message)s",
                "datefmt": "%H:%M:%S"
            }
        },
        "handlers": {},
        "root": {  # root logger - 所有子logger都会继承这个配置
            "level": log_level,
            "handlers": []
        }
    }
    
    # 控制台处理器
    if enable_console:
        config["handlers"]["console"] = {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        }
        # 添加到root logger，所有子logger自动继承
        config["root"]["handlers"].append("console")
    
    # 文件处理器
    if enable_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "detailed",
            "filename": str(log_file_path),
            "maxBytes": max_bytes,
            "backupCount": backup_count,
            "encoding": "utf-8"
        }
        # 添加到root logger，所有子logger自动继承
        config["root"]["handlers"].append("file")
    
    # 错误日志文件处理器
    if enable_file:
        error_log_file = log_dir_path / f"error_{datetime.now().strftime('%Y%m%d')}.log"
        config["handlers"]["error_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": str(error_log_file),
            "maxBytes": max_bytes,
            "backupCount": backup_count,
            "encoding": "utf-8"
        }
        # 添加到root logger，所有子logger自动继承
        config["root"]["handlers"].append("error_file")
    
    # 应用配置
    logging.config.dictConfig(config)
    
    # 为所有格式化器设置中国时区
    china_formatter = ChinaTimeFormatter()
    for handler in logging.root.handlers:
        if handler.formatter:
            handler.formatter.formatTime = china_formatter.formatTime
    
    # 记录配置信息
    logger = logging.getLogger(__name__)
    logger.info(f"日志系统已初始化 - 级别: {log_level}")
    if enable_file and log_file_path:
        error_log_file = log_dir_path / f"error_{datetime.now().strftime('%Y%m%d')}.log"
        logger.info(f"日志文件: {log_file_path}")
        logger.info(f"错误日志文件: {error_log_file}")


def get_logger(name: str = None) -> logging.Logger:
    """
    获取指定名称的logger
    
    Args:
        name: logger名称，如果为None则返回root logger
    
    Returns:
        Logger实例
    """
    return logging.getLogger(name)


def setup_default_logging():
    """
    使用默认配置设置日志系统
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_dir = os.getenv("LOG_DIR", "logs")
    
    setup_logging(
        log_level=log_level,
        log_dir=log_dir,
        enable_console=True,
        enable_file=False  # 禁用文件日志输出
    )


# 便捷的日志记录函数
def log_function(func):
    """
    装饰器：记录函数调用
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"调用函数: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"函数 {func.__name__} 执行成功")
            return result
        except Exception as e:
            logger.error(f"函数 {func.__name__} 执行失败: {str(e)}")
            raise
    return wrapper


if __name__ == "__main__":
    # 测试日志配置
    setup_default_logging()
    
    # 测试不同模块的日志
    rag_logger = get_logger("rag")
    agent_logger = get_logger("agent")
    api_logger = get_logger("api")
    
    rag_logger.info("RAG模块日志测试")
    agent_logger.warning("Agent模块警告测试")
    api_logger.error("API模块错误测试")
