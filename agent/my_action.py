from action.include import *
from action.log import MaaLog_Debug, MaaLog_Info
from action.input import (
    win32_mouse_left_down, 
    win32_mouse_left_up, 
    convert_maa_coordinates, 
    simple_mouse_click
)

@AgentServer.custom_action("sandbox_runtimes")
class SandboxRuntimesAction(CustomAction):
    """
    沙盒运行次数统计动作
    """
    
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        global Sandbox_Runtimes  # 声明使用全局变量
        
        Sandbox_Runtimes = Sandbox_Runtimes + 1
        MaaLog_Info(f"静默沙盒运行次数：{Sandbox_Runtimes}")  # f-string格式化
        
        return CustomAction.RunResult(success=True)

@AgentServer.custom_action("custom_mouse_left_down")
class CustomMouseLeftDownAction(CustomAction):
    """
    自定义鼠标左键按下动作
    使用Win32 API实现
    """
    
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        MaaLog_Debug("custom_mouse_left_down 动作开始执行")
        
        try:
            MaaLog_Debug("执行鼠标左键按下操作")
            
            # 使用Win32 API执行鼠标左键按下
            result = win32_mouse_left_down()
            
            if result:
                MaaLog_Debug("鼠标左键按下操作执行成功")
                MaaLog_Debug("==========================================\n")
                return CustomAction.RunResult(success=True)
            else:
                MaaLog_Debug("鼠标左键按下操作执行失败")
                MaaLog_Debug("==========================================\n")
                return CustomAction.RunResult(success=False)
                
        except Exception as e:
            MaaLog_Debug(f"custom_mouse_left_down 动作执行时发生异常: {e}")
            traceback.print_exc()
            MaaLog_Debug("==========================================\n")
            return CustomAction.RunResult(success=False)

@AgentServer.custom_action("myClick")
class MyCustomAction(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        MaaLog_Debug("myClick")
        regin = argv.box
        x = regin.x + regin.w/2
        y = regin.y + regin.h/2

        params = {}
        
        # 获取鼠标按钮参数，默认为左键
        button =  "left"
        # 获取重复点击相关参数
        repeat = 0
        delay = 0.5
        
        MaaLog_Debug(f"点击配置: 按钮={button}, 重复次数={repeat}, 延迟={delay}秒")

        screen_x, screen_y = convert_maa_coordinates(x, y)
        MaaLog_Debug(f"转换后屏幕坐标: ({screen_x}, {screen_y})")
        
        # 执行点击
        result = simple_mouse_click(screen_x, screen_y, button=button, repeat=repeat, delay=delay)
        
        # 返回执行结果
        if result:
            MaaLog_Debug(f"鼠标点击操作执行成功: ({screen_x}, {screen_y}) 按钮={button} 重复={repeat}次")
            MaaLog_Debug("==========================================\n")
            return CustomAction.RunResult(success=True)
        else:
            MaaLog_Debug("鼠标点击操作执行失败")
            MaaLog_Debug("==========================================\n")
            return CustomAction.RunResult(success=False)

@AgentServer.custom_action("custom_mouse_left_up")
class CustomMouseLeftUpAction(CustomAction):
    """
    自定义鼠标左键抬起动作
    使用Win32 API实现
    """
    
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        MaaLog_Debug("custom_mouse_left_up 动作开始执行")
        
        try:
            MaaLog_Debug("执行鼠标左键抬起操作")
            
            # 使用Win32 API执行鼠标左键抬起
            result = win32_mouse_left_up()
            
            if result:
                MaaLog_Debug("鼠标左键抬起操作执行成功")
                MaaLog_Debug("==========================================\n")
                return CustomAction.RunResult(success=True)
            else:
                MaaLog_Debug("鼠标左键抬起操作执行失败")
                MaaLog_Debug("==========================================\n")
                return CustomAction.RunResult(success=False)
                
        except Exception as e:
            MaaLog_Debug(f"custom_mouse_left_up 动作执行时发生异常: {e}")
            traceback.print_exc()
            MaaLog_Debug("==========================================\n")
            return CustomAction.RunResult(success=False)