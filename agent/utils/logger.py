import os
import sys
from loguru import logger

def setup_logger(log_dir=None, console_level="INFO", file_level="DEBUG"):
    """配置 loguru 日志记录器
    
    Args:
        log_dir (str): 日志目录路径，默认使用 ./debug/custom
        console_level (str): 控制台日志级别，默认 INFO
        file_level (str): 文件日志级别，默认 DEBUG
    
    Returns:
        logger: 配置好的日志记录器
    """
    # 设置默认日志目录
    if log_dir is None:
        log_dir = os.path.join(os.getcwd(), "debug/custom")

    # 尝试创建日志目录（失败时回退到用户目录）
    try:
        os.makedirs(log_dir, exist_ok=True)
    except PermissionError as e:
        print(f"警告: 无法创建日志目录 {log_dir}: {e}", file=sys.stderr)
        log_dir = os.path.join(os.path.expanduser("~"), "logs")
        os.makedirs(log_dir, exist_ok=True)

    # 移除默认处理器
    logger.remove()

    # 控制台日志配置
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        colorize=True,
        level=console_level,
    )

    # 文件日志配置
    logger.add(
        os.path.join(log_dir, "app_{time:YYYY-MM-DD}.log"),
        rotation="00:00",  # 每天轮换
        retention="14 days",  # 保留2周
        compression="zip",  # 压缩旧日志
        level=file_level,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        encoding="utf-8",
        enqueue=True,  # 异步写入
        backtrace=True,  # 记录异常堆栈
        diagnose=True,  # 显示变量值
    )

    return logger

# 全局日志记录器（可通过环境变量配置级别）
custom_logger = setup_logger(
    console_level=os.getenv("LOG_CONSOLE_LEVEL", "INFO"),
    file_level=os.getenv("LOG_FILE_LEVEL", "DEBUG"),
)