import sys
import os
import traceback
import time  # 添加time导入

# 添加DLL路径到PATH环境变量
def setup_dll_path():
    # 获取当前脚本所在目录（agent目录）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取父目录（项目根目录，包含所有DLL文件）
    dll_dir = os.path.dirname(current_dir)
    
    print(f"当前目录: {current_dir}")
    print(f"DLL目录: {dll_dir}")
    
    # 检查关键DLL文件是否存在
    key_dlls = [
        "MaaFramework.dll",
        "MaaAgentServer.dll", 
        "MaaToolkit.dll"
    ]
    
    for dll_name in key_dlls:
        dll_path = os.path.join(dll_dir, dll_name)
        if os.path.exists(dll_path):
            print(f"✅ 找到 {dll_name}: {dll_path}")
        else:
            print(f"❌ 未找到 {dll_name}: {dll_path}")
    
    # 将DLL目录添加到PATH的最前面
    old_path = os.environ.get("PATH", "")
    new_path = dll_dir + os.pathsep + old_path
    os.environ["PATH"] = new_path
    print(f"已将DLL目录添加到PATH: {dll_dir}")
    
    # 也设置其他可能需要的环境变量
    os.environ["MAA_LIBRARY_PATH"] = dll_dir
    
    return dll_dir

# 在导入MaaFramework之前设置DLL路径
dll_dir = setup_dll_path()

try:
    # 现在尝试导入MaaFramework模块
    from maa.agent.agent_server import AgentServer
    from maa.toolkit import Toolkit
    print("✅ MaaFramework 模块导入成功")
except Exception as e:
    print(f"❌ MaaFramework 模块导入失败: {e}")
    traceback.print_exc()
    sys.exit(1)

# 导入自定义模块
try:
    import my_reco
    from action import input, log
    from server import server
    print("✅ 自定义模块导入成功")
except Exception as e:
    print(f"❌ 自定义模块导入失败: {e}")
    traceback.print_exc()
    sys.exit(1)


def main():
    custom_server = None
    
    try:
        print("开始初始化 MaaFramework...")
        # 使用相对于DLL目录的路径
        Toolkit.init_option(dll_dir)
        print("MaaFramework 初始化完成")

        socket_id = sys.argv[-1]
        print(f"接收到 socket_id: {socket_id}")

        print("开始启动 AgentServer...")
        AgentServer.start_up(socket_id)
        print("AgentServer 启动成功")
        
        # 等待AgentServer完全启动
        print("等待 AgentServer 完全启动...")
        time.sleep(2)
        print("AgentServer 启动等待完成")
        
        # 现在启动CustomServer后台服务
        print("开始启动 CustomServer...")
        custom_server = server.get_custom_server()
        custom_server.start()
        print("CustomServer 启动成功")
        
        print("开始等待连接...")
        
        # AgentServer.join() 会阻塞直到连接结束
        # 在此期间，CustomServer在后台线程中持续运行
        AgentServer.join()
        print("AgentServer 连接结束")
        
        # 清理资源
        print("开始清理资源...")
        if custom_server:
            custom_server.stop()
        AgentServer.shut_down()
        print("所有服务关闭完成")

    except Exception as e:
        print(f"服务启动失败: {e}")
        traceback.print_exc()
        
        # 确保在出错时也能清理资源
        try:
            if custom_server:
                custom_server.stop()
        except:
            pass
        
        try:
            AgentServer.shut_down()
        except:
            pass
        
        sys.exit(1)


if __name__ == "__main__":
    main()