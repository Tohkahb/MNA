import os
import sys
from pathlib import Path
import json
from typing import Dict, Any, Optional
from typing import List, Tuple
import subprocess

try:
    from utils import logger
except ImportError:
    # 如果logger不存在，创建一个简单的logger
    import logging

    logging.basicConfig(
        format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO
    )
    logger = logging

# 新增工作目录设置
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
os.chdir(parent_dir)
logger.info(f"工作目录已设置为: {parent_dir}")
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

DEFAULT_CONFIG = {
    "enable_pip_update": True,
    "enable_pip_install": True,
    "last_version": "unknown",
    "mirror": "https://mirrors.ustc.edu.cn/pypi/simple",
    "backup_mirrors": [
        "https://pypi.tuna.tsinghua.edu.cn/simple",
        "https://mirrors.cloud.tencent.com/pypi/simple/",
        "https://pypi.org/simple",
    ],
}

def read_pip_config() -> Dict[str, Any]:
    """读取 pip 配置文件，不存在则创建并返回默认配置"""
    config_path = Path("./config/pip_config.json")
    config_path.parent.mkdir(exist_ok=True)
    
    if not config_path.exists():
        config_path.write_text(json.dumps(DEFAULT_CONFIG, indent=4), encoding="utf-8")
        return DEFAULT_CONFIG.copy()
    
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning(f"读取配置失败: {str(e)}，使用默认配置")
        return DEFAULT_CONFIG.copy()

def update_pip(config: Dict[str, Any]):
    """使用配置镜像源更新pip"""
    mirrors = [config["mirror"]] + config["backup_mirrors"]
    for mirror in mirrors:
        try:
            cmd = [
                sys.executable, "-m", "pip", "install", "--upgrade", "pip",
                "-i", mirror, "--trusted-host", mirror.split("/")[2]
            ]
            subprocess.run(cmd, check=True)
            logger.info("pip更新成功")
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(f"镜像 {mirror} 更新pip失败：{e.stderr}")
    return False

def get_available_mirror(pip_config: dict) -> str:
    """检查镜像源可用性并返回一个可用的镜像源"""
    mirrors = [pip_config.get("mirror")] + pip_config.get("backup_mirrors", [])
    for mirror in mirrors:
        try:
            logger.info(f"尝试连接镜像源: {mirror}")
            response = subprocess.run(
                [sys.executable, "-m", "pip", "list", "-i", mirror],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
            if response.returncode == 0:
                logger.info(f"镜像源可用: {mirror}")
                return mirror
        except Exception:
            logger.warning(f"镜像源不可用: {mirror}")
    logger.error("所有镜像源都不可用")
    return None

def install_requirements(config: Dict[str, Any], req_file: str = "requirements.txt") -> bool:
    """新版依赖安装函数"""
    req_path = Path(req_file)
    if not req_path.exists():
        logger.error(f"{req_file} 不存在")
        return False

    mirror = get_available_mirror(config)
    if not mirror:
        logger.error("没有可用的镜像源")
        return False

    try:
        cmd = [
            sys.executable, "-m", "pip", "install",
            "-r", str(req_path),
            "--no-warn-script-location",
            "-i", mirror,
            "--trusted-host", mirror.split("/")[2]
        ]
        subprocess.run(cmd, check=True)
        logger.info("依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"安装失败: {e.stderr}")
    except Exception as e:
        logger.exception("未知错误")
    return False

# 修改检查安装依赖函数
def check_and_install_dependencies(config: Dict[str, Any]):
    """综合检查安装依赖和版本"""
    try:
        # 更新pip
        if config["enable_pip_update"]:
            if not update_pip(config):
                logger.error("pip更新失败，继续尝试安装依赖")
        
        # 读取接口版本
        interface_path = Path("./interface.json")  
        
        if not interface_path.exists():
            logger.warning("未找到interface.json文件")
            return False
            
        version = json.loads(interface_path.read_text(encoding="utf-8"))["version"]
        
        # 版本检查逻辑
        if config["enable_pip_install"]:
            if config["last_version"] == "unknown" or config["last_version"] != version:
                success = install_requirements(config)
                if success:
                    update_last_version(version)
                return success
            logger.info("当前版本依赖已是最新")
        return True
    except Exception as e:
        logger.exception(f"依赖检查失败: {str(e)}")
        return False

def update_last_version(version: str):
    """更新配置文件版本号"""
    config_path = Path("./config/pip_config.json")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["last_version"] = version
    config_path.write_text(json.dumps(config, indent=4), encoding="utf-8")

def get_requirements() -> List[str]:
    """从requirements.txt获取依赖列表"""
    requirements = Path("requirements.txt")
    if not requirements.exists():
        raise FileNotFoundError("requirements.txt不存在")
    return [line.strip() for line in requirements.read_text(encoding="utf-8").splitlines() 
            if line.strip() and not line.startswith("#")]

def setup_environment() -> bool:
    """环境初始化并返回是否成功"""
    config = read_pip_config()
    if not check_and_install_dependencies(config):
        logger.error("依赖安装失败，请检查日志")
        return False
    return True

def agent():
    try:
        from utils import logger
        from maa.agent.agent_server import AgentServer
        from maa.toolkit import Toolkit
        import custom
        
        Toolkit.init_option("./")

        socket_id = sys.argv[-1]

        AgentServer.start_up(socket_id)
        AgentServer.join()
        AgentServer.shut_down()

    except Exception as e:
        logger.exception("AgentServer 启动失败: %s", str(e))
        sys.exit(1)

def main():
    setup_environment()
    agent()

if __name__ == "__main__":
    main()