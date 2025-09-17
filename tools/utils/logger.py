import logging
import os
from datetime import datetime
from typing import Optional

def setup_logger(name: str = "llm4cybersecurity", 
                level: str = "INFO",
                log_file: Optional[str] = None,
                console_output: bool = True) -> logging.Logger:
    """设置日志系统"""
    
    # 创建日志目录
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    # 设置日志级别
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # 配置根日志器以捕获所有模块的日志
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 清除已有的处理器，避免重复输出
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台输出
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        root_logger.addHandler(console_handler)
    
    # 文件输出
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)
    
    # 返回指定名称的日志器
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    return logger

def get_default_log_file() -> str:
    """获取默认日志文件路径"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d")
    return os.path.join(log_dir, f"update_{timestamp}.log")