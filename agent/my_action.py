from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

import time
import ctypes
import win32con
import win32gui
import win32process
import win32api
import sys
import os
import traceback
import json
import win32ui
from ctypes import windll, wintypes, byref, sizeof
from PIL import Image, ImageGrab
import numpy as np

import re

Enable_MaaLog_Debug = 0
Enable_MaaLog_Info = 1

Sandbox_Runtimes = 0

def MaaLog_Debug(message):
    if Enable_MaaLog_Debug:
        print(message)
    # End if
# End def

def MaaLog_Info(message):
    if Enable_MaaLog_Info:
        print(message)
    # End if
# End def

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
    # End def
# End class

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
            # End if
                
        except Exception as e:
            MaaLog_Debug(f"custom_mouse_left_down 动作执行时发生异常: {e}")
            traceback.print_exc()
            MaaLog_Debug("==========================================\n")
            return CustomAction.RunResult(success=False)
        # End try
    # End def
# End class

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
        # End if
    # End def
# End class

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
            # End if
                
        except Exception as e:
            MaaLog_Debug(f"custom_mouse_left_up 动作执行时发生异常: {e}")
            traceback.print_exc()
            MaaLog_Debug("==========================================\n")
            return CustomAction.RunResult(success=False)
        # End try
    # End def
# End class

def win32_mouse_left_down():
    """
    使用Win32 API执行鼠标左键按下操作
    使用当前鼠标位置
    
    返回:
        bool: 是否成功
    """
    try:
        MaaLog_Debug("执行Win32鼠标左键按下")
        
        # 获取当前鼠标位置
        current_pos = win32api.GetCursorPos()
        screen_x, screen_y = current_pos[0], current_pos[1]
        MaaLog_Debug(f"当前鼠标位置: ({screen_x}, {screen_y})")
        
        # 确保目标窗口获得焦点
        hwnd = find_game_window()
        if hwnd == 0:
            MaaLog_Debug("错误: 无法找到游戏窗口")
            return False
        # End if
            
        # 激活窗口并等待
        MaaLog_Debug(f"激活窗口，句柄: {hwnd}")
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.2)
        
        # 验证窗口是否已激活
        current_hwnd = win32gui.GetForegroundWindow()
        if current_hwnd != hwnd:
            MaaLog_Debug(f"警告: 窗口激活可能失败。期望: {hwnd}, 实际: {current_hwnd}")
        # End if
        
        # 使用mouse_event发送鼠标左键按下事件
        MaaLog_Debug(f"在位置 ({screen_x}, {screen_y}) 发送鼠标左键按下事件")
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        
        MaaLog_Debug("鼠标左键按下发送成功")
        return True
        
    except Exception as e:
        MaaLog_Debug(f"Win32鼠标左键按下操作失败: {e}")
        traceback.print_exc()
        return False
    # End try
# End def


def win32_mouse_left_up():
    """
    使用Win32 API执行鼠标左键抬起操作
    使用当前鼠标位置
    
    返回:
        bool: 是否成功
    """
    try:
        MaaLog_Debug("执行Win32鼠标左键抬起")
        
        # 获取当前鼠标位置
        current_pos = win32api.GetCursorPos()
        screen_x, screen_y = current_pos[0], current_pos[1]
        MaaLog_Debug(f"当前鼠标位置: ({screen_x}, {screen_y})")
        
        # 确保目标窗口获得焦点
        hwnd = find_game_window()
        if hwnd == 0:
            MaaLog_Debug("错误: 无法找到游戏窗口")
            return False
        # End if
            
        # 激活窗口并等待
        MaaLog_Debug(f"激活窗口，句柄: {hwnd}")
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.2)
        
        # 验证窗口是否已激活
        current_hwnd = win32gui.GetForegroundWindow()
        if current_hwnd != hwnd:
            MaaLog_Debug(f"警告: 窗口激活可能失败。期望: {hwnd}, 实际: {current_hwnd}")
        # End if
        
        # 使用mouse_event发送鼠标左键抬起事件
        MaaLog_Debug(f"在位置 ({screen_x}, {screen_y}) 发送鼠标左键抬起事件")
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        
        MaaLog_Debug("鼠标左键抬起发送成功")
        return True
        
    except Exception as e:
        MaaLog_Debug(f"Win32鼠标左键抬起操作失败: {e}")
        traceback.print_exc()
        return False
    # End try
# End def

def find_game_window():
    """查找少女前线游戏窗口"""
    try:
        hwnd = win32gui.FindWindow(None, "少女前线")
        if hwnd == 0:
            # 尝试模糊匹配
            MaaLog_Debug("未能精确匹配'少女前线'窗口，尝试模糊匹配...")
            all_windows = []
            win32gui.EnumWindows(lambda h, param: param.append((h, win32gui.GetWindowText(h))), all_windows)
            
            MaaLog_Debug(f"找到的窗口列表:")
            for h, title in all_windows:
                if len(title) > 0:  # 只显示有标题的窗口
                    MaaLog_Debug(f"  - 窗口句柄: {h}, 标题: '{title}'")
                    
                    if "少女前线" in title or "Mabinogi" in title:
                        hwnd = h
                        MaaLog_Debug(f"  --> 匹配到少女前线窗口!")
                        break
                    # End if
                # End if
            # End for
        # End if
        
        if hwnd != 0:
            # 检查窗口是否可见
            if win32gui.IsWindowVisible(hwnd):
                # 获取窗口位置和大小
                rect = win32gui.GetWindowRect(hwnd)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                
                # 获取客户区大小
                client_rect = win32gui.GetClientRect(hwnd)
                client_width = client_rect[2]
                client_height = client_rect[3]
                
                MaaLog_Debug(f"找到少女前线窗口，句柄: {hwnd}")
                MaaLog_Debug(f"窗口位置: ({rect[0]}, {rect[1]}, {rect[2]}, {rect[3]})")
                MaaLog_Debug(f"窗口大小: {width}x{height}")
                MaaLog_Debug(f"客户区大小: {client_width}x{client_height}")
                
                return hwnd
            else:
                MaaLog_Debug(f"警告: 找到少女前线窗口(句柄: {hwnd})但窗口不可见")
            # End if
        # End if
        
        MaaLog_Debug("警告: 未找到少女前线窗口，将尝试查找其他可能的游戏窗口")
        
        # 尝试寻找任何大窗口，可能是游戏窗口
        all_windows = []
        win32gui.EnumWindows(lambda h, param: param.append((h, win32gui.GetWindowText(h))), all_windows)
        
        for h, title in all_windows:
            if not title:  # 跳过无标题窗口
                continue
            # End if
                
            # 检查窗口是否可见且大小合适
            if win32gui.IsWindowVisible(h):
                rect = win32gui.GetWindowRect(h)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                
                # 游戏窗口通常较大
                if width > 400 and height > 300:
                    MaaLog_Debug(f"发现可能的游戏窗口: 句柄={h}, 标题='{title}', 大小={width}x{height}")
                    
                    # 询问是否使用此窗口
                    hwnd = h
                    MaaLog_Debug(f"将使用窗口: 句柄={hwnd}, 标题='{title}'")
                    return hwnd
                # End if
            # End if
        # End for
        
        # 如果还是找不到合适的窗口，使用当前活动窗口
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        
        MaaLog_Debug(f"未找到符合条件的窗口，将使用当前活动窗口:")
        MaaLog_Debug(f"句柄={hwnd}, 标题='{window_title}', 大小={width}x{height}")
        return hwnd
            
    except Exception as e:
        MaaLog_Debug(f"查找游戏窗口时出错: {e}")
        traceback.print_exc()
        
        # 出错时使用当前活动窗口
        try:
            hwnd = win32gui.GetForegroundWindow()
            MaaLog_Debug(f"由于出错，使用当前活动窗口，句柄: {hwnd}")
            return hwnd
        except:
            MaaLog_Debug("无法获取任何窗口，返回0")
            return 0
        # End try
    # End try
# End def

def convert_maa_coordinates(x, y, hwnd=None, maa_width=1280, maa_height=720, x_correction=1):
    """将MAA中的坐标转换为游戏窗口中的屏幕绝对坐标
    
    参数:
        x, y: MAA中的相对坐标（基于720P缩放后的坐标）
        hwnd: 游戏窗口句柄，如果为None则会尝试查找
        maa_width: MAA使用的宽度，默认1280
        maa_height: MAA使用的高度，默认720
        x_correction: x轴额外修正系数，默认1
        
    返回:
        tuple: (screen_x, screen_y) 屏幕绝对坐标
    """
    try:
        # 如果没有提供窗口句柄，查找游戏窗口
        if hwnd is None:
            hwnd = find_game_window()
            if hwnd == 0:
                MaaLog_Debug("错误: 无法找到游戏窗口")
                return x, y  # 如果找不到窗口，直接返回原始坐标
            # End if
        # End if
        
        # 获取窗口客户区在屏幕上的位置
        client_point = wintypes.POINT(0, 0)
        windll.user32.ClientToScreen(hwnd, byref(client_point))
        client_x, client_y = client_point.x, client_point.y
        
        # 获取客户区大小
        client_rect = win32gui.GetClientRect(hwnd)
        client_width, client_height = client_rect[2], client_rect[3]
        
        MaaLog_Debug(f"客户区左上角屏幕坐标: ({client_x}, {client_y})")
        MaaLog_Debug(f"客户区实际大小: {client_width}x{client_height}")
        MaaLog_Debug(f"MAA使用分辨率: {maa_width}x{maa_height}")
        
        # 计算缩放比例
        scale_x = client_width / maa_width
        scale_y = client_height / maa_height
        
        # 应用x轴修正系数
        corrected_scale_x = scale_x * x_correction
        
        MaaLog_Debug(f"基础缩放比例: X轴={scale_x:.3f}, Y轴={scale_y:.3f}")
        MaaLog_Debug(f"X轴修正系数: {x_correction}")
        MaaLog_Debug(f"修正后缩放比例: X轴={corrected_scale_x:.3f}, Y轴={scale_y:.3f}")
        
        # 根据缩放比例转换坐标
        real_x = int(x * corrected_scale_x)
        real_y = int(y * scale_y)
        MaaLog_Debug(f"MAA坐标({x}, {y}) -> 客户区相对坐标({real_x}, {real_y})")
        
        # 计算绝对坐标
        screen_x = client_x + real_x
        screen_y = client_y + real_y
        MaaLog_Debug(f"客户区相对坐标({real_x}, {real_y}) -> 屏幕绝对坐标({screen_x}, {screen_y})")
        
        return screen_x, screen_y
    
    except Exception as e:
        MaaLog_Debug(f"坐标转换失败: {e}")
        traceback.print_exc()
        return x, y  # 出错时返回原始坐标
    # End try
# End def


# 简化的模拟鼠标点击函数 - 修复点击不正确的问题
def simple_mouse_click(x, y, button="left", repeat=1, delay=0.5):
    """使用绝对坐标直接点击
    
    参数:
        x, y: 屏幕绝对坐标
        button: 鼠标按钮，"left", "right", "middle"
        repeat: 重复执行次数
        delay: 每次执行间的延迟(秒)
    
    返回:
        bool: 是否成功
    """
    try:
        # 确保坐标是整数
        x, y = int(x), int(y)
        
        # 打印点击信息
        MaaLog_Debug(f"执行点击操作: 屏幕坐标({x}, {y}), 按钮={button}, 重复={repeat}次")
        
        # 获取屏幕大小用于安全检查
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        MaaLog_Debug(f"屏幕大小: {screen_width}x{screen_height}")
        
        # 确保坐标在屏幕范围内
        if x < 0 or x >= screen_width or y < 0 or y >= screen_height:
            MaaLog_Debug(f"警告: 坐标({x}, {y})超出屏幕范围，将进行调整")
            x = max(0, min(x, screen_width - 1))
            y = max(0, min(y, screen_height - 1))
            MaaLog_Debug(f"调整后坐标: ({x}, {y})")
        # End if
        
        # 移动鼠标到指定位置
        win32api.SetCursorPos((x, y))
        time.sleep(0.1)
        
        # 根据按钮类型执行点击
        if button.lower() == "left":
            MaaLog_Debug(f"执行左键点击")
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            
            # 重复执行
            for i in range(repeat - 1):
                MaaLog_Debug(f"重复执行第 {i+2}/{repeat} 次左键点击...")
                time.sleep(delay)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                time.sleep(0.05)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            # End for
                
        elif button.lower() == "right":
            MaaLog_Debug(f"执行右键点击")
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
            
            # 重复执行
            for i in range(repeat - 1):
                MaaLog_Debug(f"重复执行第 {i+2}/{repeat} 次右键点击...")
                time.sleep(delay)
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
                time.sleep(0.05)
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
            # End for
                
        elif button.lower() == "middle":
            MaaLog_Debug(f"执行中键点击")
            win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0)
            
            # 重复执行
            for i in range(repeat - 1):
                MaaLog_Debug(f"重复执行第 {i+2}/{repeat} 次中键点击...")
                time.sleep(delay)
                win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0)
                time.sleep(0.05)
                win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0)
            # End for
        # End if
        
        return True
        
    except Exception as e:
        MaaLog_Debug(f"鼠标点击操作失败: {e}")
        traceback.print_exc()
        return False
    # End try
# End def