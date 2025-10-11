from .include import *
import json
import requests

# Load config.py
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
from config import get_telegram_config, is_telegram_configured

#######################################################################################################################################################################################
################################################################################ Part I : Registration ################################################################################
#######################################################################################################################################################################################

class TelegramNotifier:
    """
    Telegram通知器
    """
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, message):
        """发送消息到Telegram"""
        url = f"{self.base_url}/sendMessage"
        data = {
            'chat_id': self.chat_id,
            'text': message
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                MaaLog_Debug(f"Telegram消息发送成功: {message}")
                return True
            else:
                MaaLog_Debug(f"Telegram消息发送失败: {response.text}")
                return False
        except Exception as e:
            MaaLog_Debug(f"发送Telegram消息时出错: {e}")
            return False

@AgentServer.custom_action("parametric_log")
class ParametricLogAction(CustomAction):
    """
    支持从custom_action_param中读取日志消息模板和参数
    """
    
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        try:
            # 从custom_action_param获取参数
            param = argv.custom_action_param
            
            # 无param：输出默认消息
            if not param:
                MaaLog_Info("默认日志消息")
                return CustomAction.RunResult(success=True)
            
            # 调试：输出param的类型和内容
            MaaLog_Debug(f"param类型: {type(param)}, 内容: {param}")
            
            # 尝试解析JSON字符串
            if isinstance(param, str):
                try:
                    # 尝试将字符串解析为JSON
                    parsed_param = json.loads(param)
                    param = parsed_param
                    MaaLog_Debug(f"成功解析JSON，类型: {type(param)}")
                except json.JSONDecodeError:
                    # 如果不是JSON，直接作为字符串输出
                    MaaLog_Info(param)
                    return CustomAction.RunResult(success=True)
            
            # 如果param是字典：进行参数化处理
            if isinstance(param, dict):
                log_type = param.get('type', 'info')
                message_template = param.get('message', '默认日志消息')
                parameters = param.get('parameters', {})
                
                MaaLog_Debug(f"开始处理参数化日志 - 类型: {log_type}, 模板: {message_template}, 参数: {parameters}")
                
                # 处理特殊参数
                processed_params = self._process_parameters(parameters)
                MaaLog_Debug(f"处理后的参数: {processed_params}")
                
                # 格式化消息
                try:
                    formatted_message = message_template.format(**processed_params)
                    MaaLog_Debug(f"格式化后的消息: {formatted_message}")
                except KeyError as e:
                    MaaLog_Debug(f"消息模板格式化失败，缺少参数: {e}")
                    formatted_message = message_template
                except Exception as e:
                    MaaLog_Debug(f"消息格式化异常: {e}")
                    formatted_message = message_template
                
                # 输出日志
                if log_type.lower() == 'debug':
                    MaaLog_Debug(formatted_message)
                else:
                    MaaLog_Info(formatted_message)
            else:
                # 其他类型直接转字符串输出
                MaaLog_Info(str(param))
            
            return CustomAction.RunResult(success=True)
            
        except Exception as e:
            MaaLog_Debug(f"ParametricLogAction执行异常: {e}")
            import traceback
            MaaLog_Debug(f"异常堆栈: {traceback.format_exc()}")
            return CustomAction.RunResult(success=False)
    
    def _process_parameters(self, parameters: dict) -> dict:
        """
        处理特殊参数，支持动态值
        """
        global Task_Counter
        
        processed = {}
        
        for key, value in parameters.items():
            MaaLog_Debug(f"处理参数 {key}: {value} (类型: {type(value)})")
            
            if isinstance(value, str):
                # 处理特殊占位符
                if value == "{Task_Counter}":
                    processed[key] = Task_Counter
                    MaaLog_Debug(f"替换 {key} = {Task_Counter}")
                elif value == "{increment_Task_Counter}":
                    Task_Counter += 1
                    processed[key] = Task_Counter
                    MaaLog_Debug(f"递增并替换 {key} = {Task_Counter}")
                else:
                    processed[key] = value
            else:
                processed[key] = value
        
        return processed

@AgentServer.custom_action("parametric_telegram")
class ParametricTelegramAction(CustomAction):
    """
    支持从custom_action_param中读取消息模板和参数，并发送到Telegram
    """
    
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        try:
            # 获取Telegram配置
            bot_token, chat_id = get_telegram_config()
            
            if not bot_token or not chat_id:
                MaaLog_Debug("Telegram配置未设置，无法发送消息")
                return CustomAction.RunResult(success=False)
            
            # 创建Telegram通知器
            notifier = TelegramNotifier(bot_token, chat_id)
            
            # 从custom_action_param获取参数
            param = argv.custom_action_param
            
            # 无param：发送默认消息
            if not param:
                return CustomAction.RunResult(success=notifier.send_message("默认Telegram消息"))
            
            # 调试：输出param的类型和内容
            MaaLog_Debug(f"Telegram param类型: {type(param)}, 内容: {param}")
            
            # 尝试解析JSON字符串
            if isinstance(param, str):
                try:
                    # 尝试将字符串解析为JSON
                    parsed_param = json.loads(param)
                    param = parsed_param
                    MaaLog_Debug(f"成功解析JSON，类型: {type(param)}")
                except json.JSONDecodeError:
                    # 如果不是JSON，直接作为字符串发送
                    return CustomAction.RunResult(success=notifier.send_message(param))
            
            # 如果param是字典：进行参数化处理
            if isinstance(param, dict):
                message_template = param.get('message', '默认Telegram消息')
                parameters = param.get('parameters', {})
                
                MaaLog_Debug(f"开始处理参数化Telegram消息 - 模板: {message_template}, 参数: {parameters}")
                
                # 处理特殊参数
                processed_params = self._process_parameters(parameters)
                MaaLog_Debug(f"处理后的参数: {processed_params}")
                
                # 格式化消息
                try:
                    formatted_message = message_template.format(**processed_params)
                    MaaLog_Debug(f"格式化后的消息: {formatted_message}")
                except KeyError as e:
                    MaaLog_Debug(f"消息模板格式化失败，缺少参数: {e}")
                    formatted_message = message_template
                except Exception as e:
                    MaaLog_Debug(f"消息格式化异常: {e}")
                    formatted_message = message_template
                
                # 发送到Telegram
                return CustomAction.RunResult(success=notifier.send_message(formatted_message))
            else:
                # 其他类型直接转字符串发送
                return CustomAction.RunResult(success=notifier.send_message(str(param)))
            
        except Exception as e:
            MaaLog_Debug(f"ParametricTelegramAction执行异常: {e}")
            import traceback
            MaaLog_Debug(f"异常堆栈: {traceback.format_exc()}")
            return CustomAction.RunResult(success=False)
    
    def _process_parameters(self, parameters: dict) -> dict:
        """
        处理特殊参数，支持动态值
        """
        global Task_Counter
        
        processed = {}
        
        for key, value in parameters.items():
            MaaLog_Debug(f"处理Telegram参数 {key}: {value} (类型: {type(value)})")
            
            if isinstance(value, str):
                # 处理特殊占位符
                if value == "{Task_Counter}":
                    processed[key] = Task_Counter
                    MaaLog_Debug(f"替换 {key} = {Task_Counter}")
                elif value == "{increment_Task_Counter}":
                    Task_Counter += 1
                    processed[key] = Task_Counter
                    MaaLog_Debug(f"递增并替换 {key} = {Task_Counter}")
                else:
                    processed[key] = value
            else:
                processed[key] = value
        
        return processed

##########################################################################################################################################################################################
################################################################################ Part II : Implementation ################################################################################
##########################################################################################################################################################################################

def MaaLog_Debug(message):
    """调试日志输出"""
    if Enable_MaaLog_Debug:
        print(f"[DEBUG] {message}")

def MaaLog_Info(message):
    """信息日志输出"""
    if Enable_MaaLog_Info:
        print(f"[INFO] {message}")

def set_debug_log(enabled):
    """设置调试日志开关"""
    global Enable_MaaLog_Debug
    Enable_MaaLog_Debug = 1 if enabled else 0

def set_info_log(enabled):
    """设置信息日志开关"""
    global Enable_MaaLog_Info
    Enable_MaaLog_Info = 1 if enabled else 0

def get_Task_Counter():
    """获取当前任务运行次数"""
    global Task_Counter
    return Task_Counter

def reset_Task_Counter():
    """重置任务运行次数"""
    global Task_Counter
    Task_Counter = 0