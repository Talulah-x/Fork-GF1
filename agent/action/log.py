from .include import *

# 日志控制开关
Enable_MaaLog_Debug = 1
Enable_MaaLog_Info = 1

def MaaLog_Debug(message):
    """调试日志输出"""
    if Enable_MaaLog_Debug:
        print(message)

def MaaLog_Info(message):
    """信息日志输出"""
    if Enable_MaaLog_Info:
        print(message)

def set_debug_log(enabled):
    """设置调试日志开关"""
    global Enable_MaaLog_Debug
    Enable_MaaLog_Debug = 1 if enabled else 0

def set_info_log(enabled):
    """设置信息日志开关"""
    global Enable_MaaLog_Info
    Enable_MaaLog_Info = 1 if enabled else 0