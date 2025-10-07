import threading
import time
import datetime
from action.log import MaaLog_Info, MaaLog_Debug
from action.include import AgentServer, CustomAction, Context

class CustomServer:
    """
    自定义服务器类
    提供后台服务和Custom Action功能
    """
    
    def __init__(self):
        """初始化CustomServer"""
        self.running = False
        self.thread = None
        MaaLog_Info("CustomServer 初始化完成")
    
    def start(self):
        """启动服务器"""
        if self.running:
            MaaLog_Info("CustomServer 已经在运行中")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_service, daemon=True)
        self.thread.start()
        MaaLog_Info("CustomServer 后台服务已启动")
    
    def stop(self):
        """停止服务器"""
        if not self.running:
            MaaLog_Info("CustomServer 未在运行")
            return
        
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        MaaLog_Info("CustomServer 后台服务已停止")
    
    def _run_service(self):
        """
        后台服务主循环
        类似于C++中的operator()
        """
        MaaLog_Info("CustomServer 后台服务循环开始运行")
        
        while self.running:
            try:
                # 获取当前时间并打印
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                MaaLog_Info(f"[CustomServer] 当前时间: {current_time}")
                
                # 等待1秒
                time.sleep(1)
                
            except Exception as e:
                MaaLog_Debug(f"CustomServer 服务循环出错: {e}")
                # 即使出错也继续运行
                time.sleep(1)
        
        MaaLog_Info("CustomServer 后台服务循环结束")
    
    def hello(self):
        """
        Hello方法，将被注册为Custom Action
        
        返回:
            str: 问候消息
        """
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Hello from CustomServer! 当前时间: {current_time}"
        MaaLog_Info(f"[CustomServer.hello] {message}")
        return message
    
    def is_running(self):
        """检查服务器是否在运行"""
        return self.running


# 创建全局CustomServer实例
custom_server_instance = CustomServer()

@AgentServer.custom_action("CustomServer.hello")
class CustomServerHelloAction(CustomAction):
    """
    CustomServer的hello方法对应的Custom Action
    """
    
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        MaaLog_Debug("CustomServer.hello Action 开始执行")
        
        try:
            message = custom_server_instance.hello()
            
            MaaLog_Debug(f"CustomServer.hello Action 执行成功: {message}")
            return CustomAction.RunResult(success=True)
            
        except Exception as e:
            MaaLog_Debug(f"CustomServer.hello Action 执行失败: {e}")
            return CustomAction.RunResult(success=False)


def get_custom_server():
    """获取全局CustomServer实例"""
    return custom_server_instance