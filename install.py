from pathlib import Path
import shutil
import sys
import json
import subprocess
import os

from configure import configure_ocr_model

working_dir = Path(__file__).parent
install_path = working_dir / Path("install")
version = len(sys.argv) > 1 and sys.argv[1] or "v0.0.1"


def install_deps():
    if not (working_dir / "deps" / "bin").exists():
        print("Please download the MaaFramework to \"deps\" first.")
        print("请先下载 MaaFramework 到 \"deps\"。")
        sys.exit(1)

    shutil.copytree(
        working_dir / "deps" / "bin",
        install_path,
        ignore=shutil.ignore_patterns(
            "*MaaDbgControlUnit*",
            "*MaaThriftControlUnit*",
            "*MaaRpc*",
            "*MaaHttp*",
        ),
        dirs_exist_ok=True,
    )
    shutil.copytree(
        working_dir / "deps" / "share" / "MaaAgentBinary",
        install_path / "MaaAgentBinary",
        dirs_exist_ok=True,
    )


def install_resource():
    configure_ocr_model()

    shutil.copytree(
        working_dir / "assets" / "resource",
        install_path / "resource",
        dirs_exist_ok=True,
    )
    shutil.copy2(
        working_dir / "assets" / "interface.json",
        install_path,
    )

    with open(install_path / "interface.json", "r", encoding="utf-8") as f:
        interface = json.load(f)

    interface["version"] = version

    with open(install_path / "interface.json", "w", encoding="utf-8") as f:
        json.dump(interface, f, ensure_ascii=False, indent=4)


def install_chores():
    shutil.copy2(
        working_dir / "README.md",
        install_path,
    )
    shutil.copy2(
        working_dir / "LICENSE",
        install_path,
    )


def build_agent():
    """使用 PyInstaller 编译 agent 为可执行文件"""
    agent_dir = working_dir / "agent"
    spec_file = agent_dir / "build.spec"
    
    if not agent_dir.exists():
        print("Warning: agent directory not found, skipping agent build.")
        return False
    
    if not spec_file.exists():
        print("Warning: build.spec not found, skipping agent build.")
        return False
    
    print("Building agent with PyInstaller...")
    
    # 切换到 agent 目录
    original_cwd = os.getcwd()
    try:
        os.chdir(agent_dir)
        
        # 运行 PyInstaller
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller", 
            "--clean", 
            "build.spec"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"PyInstaller failed with return code {result.returncode}")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
        
        print("Agent build completed successfully.")
        return True
        
    except Exception as e:
        print(f"Error building agent: {e}")
        return False
    finally:
        os.chdir(original_cwd)


def install_agent():
    """安装 agent 到安装目录"""
    # 首先尝试编译 agent
    build_success = build_agent()
    
    agent_src = working_dir / "agent"
    agent_dst = install_path / "agent"
    
    # 创建 agent 目录
    agent_dst.mkdir(parents=True, exist_ok=True)
    
    # 如果编译成功，复制编译后的可执行文件
    if build_success:
        exe_src = agent_src / "dist" / "maa_agent.exe"
        if exe_src.exists():
            dist_dst = agent_dst / "dist"
            dist_dst.mkdir(exist_ok=True)
            shutil.copy2(exe_src, dist_dst / "maa_agent.exe")
            print(f"Agent executable installed: {exe_src} -> {dist_dst / 'maa_agent.exe'}")
        else:
            print("Warning: maa_agent.exe not found after build.")
    
    # 复制其他 agent 文件（源码、配置等，如果需要的话）
    for item in agent_src.iterdir():
        if item.name in ["build", "dist", "__pycache__"]:
            continue  # 跳过编译目录和缓存
        
        dst_item = agent_dst / item.name
        if item.is_file():
            shutil.copy2(item, dst_item)
        elif item.is_dir():
            shutil.copytree(item, dst_item, dirs_exist_ok=True)


def install_tools():
    """安装工具脚本到安装目录"""
    tools_src = working_dir / "tools"
    tools_dst = install_path / "tools"
    
    if tools_src.exists():
        shutil.copytree(
            tools_src,
            tools_dst,
            dirs_exist_ok=True,
        )
        print(f"Tools installed: {tools_src} -> {tools_dst}")
    else:
        print("Warning: tools directory not found, skipping tools installation.")


if __name__ == "__main__":
    install_deps()
    install_resource()
    install_chores()
    install_agent()
    install_tools()

    print(f"Install to {install_path} successfully.")