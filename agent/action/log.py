from .include import *
import json
import requests

# Load config.py
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
from config import (get_telegram_config, is_telegram_configured, 
                   get_wechat_config, is_wechat_configured,
                   get_default_ext_notify, get_available_notifiers)

#######################################################################################################################################################################################
################################################################################ Part I : Registration ################################################################################
#######################################################################################################################################################################################

class TelegramNotifier:
    """
    Telegram notifier
    """
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, message):
        """Send message to Telegram"""
        url = f"{self.base_url}/sendMessage"
        data = {
            'chat_id': self.chat_id,
            'text': message
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                MaaLog_Debug(f"Telegram message sent successfully: {message}")
                return True
            else:
                MaaLog_Debug(f"Telegram message sending failed: {response.text}")
                return False
        except Exception as e:
            MaaLog_Debug(f"Error occurred while sending Telegram message: {e}")
            return False

class WeChatWorkNotifier:
    """
    Enterprise WeChat notifier
    """
    def __init__(self, webhook_key):
        self.webhook_key = webhook_key
        self.webhook_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={webhook_key}"
    
    def send_message(self, message, msgtype="text"):
        """Send message to Enterprise WeChat"""
        # Construct message body
        if msgtype == "text":
            data = {
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
        elif msgtype == "markdown":
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": message
                }
            }
        else:
            MaaLog_Debug(f"Unsupported message type: {msgtype}")
            return False
        
        try:
            # Send POST request
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                self.webhook_url, 
                data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    MaaLog_Debug(f"Enterprise WeChat message sent successfully: {message}")
                    return True
                else:
                    MaaLog_Debug(f"Enterprise WeChat message sending failed: {result.get('errmsg', 'Unknown error')}")
                    return False
            else:
                MaaLog_Debug(f"Enterprise WeChat HTTP request failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            MaaLog_Debug(f"Error occurred while sending Enterprise WeChat message: {e}")
            return False

class ParametricBaseAction(CustomAction):
    """
    Parametric action base class
    Provides common parameter parsing, processing and formatting functions
    """
    
    def __init__(self):
        super().__init__()
        self.action_name = self.__class__.__name__
    
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        """
        Base class run method, handles common logic
        """
        try:
            # Get parameters from custom_action_param
            param = argv.custom_action_param
            
            # Parse parameters
            parsed_param = self._parse_param(param)
            
            # Handle parametric message
            result = self._handle_parametric_message(parsed_param)
            
            return CustomAction.RunResult(success=result)
            
        except Exception as e:
            MaaLog_Debug(f"{self.action_name} execution exception: {e}")
            import traceback
            MaaLog_Debug(f"Exception stack: {traceback.format_exc()}")
            return CustomAction.RunResult(success=False)
    
    def _parse_param(self, param):
        """
        Parse parameters, support string, JSON and dictionary formats
        """
        # No param: return None
        if not param:
            MaaLog_Debug(f"{self.action_name}: No parameters, using default processing")
            return None
        
        # Debug: output param type and content
        MaaLog_Debug(f"{self.action_name} param type: {type(param)}, content: {param}")
        
        # Try to parse JSON string
        if isinstance(param, str):
            try:
                # Try to parse string as JSON
                parsed_param = json.loads(param)
                MaaLog_Debug(f"{self.action_name}: Successfully parsed JSON, type: {type(parsed_param)}")
                return parsed_param
            except json.JSONDecodeError:
                # If not JSON, return string directly
                MaaLog_Debug(f"{self.action_name}: Non-JSON string, using directly")
                return param
        
        # Return dictionary or other types directly
        return param
    
    def _process_parameters(self, parameters: dict) -> dict:
        """
        Process special parameters, support dynamic values
        """
        global Task_Counter
        
        processed = {}
        
        for key, value in parameters.items():
            MaaLog_Debug(f"{self.action_name} processing parameter {key}: {value} (type: {type(value)})")
            
            if isinstance(value, str):
                # Handle special placeholders
                if value == "{Task_Counter}":
                    processed[key] = Task_Counter
                    MaaLog_Debug(f"{self.action_name} replace {key} = {Task_Counter}")
                elif value == "{increment_Task_Counter}":
                    Task_Counter += 1
                    processed[key] = Task_Counter
                    MaaLog_Debug(f"{self.action_name} increment and replace {key} = {Task_Counter}")
                else:
                    processed[key] = value
            else:
                processed[key] = value
        
        return processed
    
    def _format_message(self, message_template: str, parameters: dict) -> str:
        """
        Format message template
        """
        try:
            # Process special parameters
            processed_params = self._process_parameters(parameters)
            MaaLog_Debug(f"{self.action_name} processed parameters: {processed_params}")
            
            # Format message
            formatted_message = message_template.format(**processed_params)
            MaaLog_Debug(f"{self.action_name} formatted message: {formatted_message}")
            return formatted_message
        except KeyError as e:
            MaaLog_Debug(f"{self.action_name} message template formatting failed, missing parameter: {e}")
            return message_template
        except Exception as e:
            MaaLog_Debug(f"{self.action_name} message formatting exception: {e}")
            return message_template
    
    def _handle_parametric_message(self, parsed_param):
        """
        Common logic for handling parametric messages
        Subclasses can override this method to customize processing logic
        """
        # No parameter case
        if parsed_param is None:
            return self._handle_default_message()
        
        # String case: process directly
        if isinstance(parsed_param, str):
            return self._handle_string_message(parsed_param)
        
        # Dictionary case: parametric processing
        if isinstance(parsed_param, dict):
            return self._handle_dict_message(parsed_param)
        
        # Other types: convert to string and process
        return self._handle_string_message(str(parsed_param))
    
    # Abstract methods, subclasses must implement
    def _handle_default_message(self):
        """Handle default message, subclasses must implement"""
        raise NotImplementedError("Subclasses must implement _handle_default_message method")
    
    def _handle_string_message(self, message: str):
        """Handle string message, subclasses must implement"""
        raise NotImplementedError("Subclasses must implement _handle_string_message method")
    
    def _handle_dict_message(self, param_dict: dict):
        """Handle dictionary parameter message, subclasses must implement"""
        raise NotImplementedError("Subclasses must implement _handle_dict_message method")

@AgentServer.custom_action("parametric_log")
class ParametricLogAction(ParametricBaseAction):
    """
    Support reading log message template and parameters from custom_action_param
    """
    
    def _handle_default_message(self):
        """Handle default message"""
        MaaLog_Info("Default log message")
        return True
    
    def _handle_string_message(self, message: str):
        """Handle string message"""
        MaaLog_Info(message)
        return True
    
    def _handle_dict_message(self, param_dict: dict):
        """Handle dictionary parameter message"""
        log_type = param_dict.get('type', 'info')
        message_template = param_dict.get('message', 'Default log message')
        parameters = param_dict.get('parameters', {})
        
        MaaLog_Debug(f"Start processing parametric log - type: {log_type}, template: {message_template}, parameters: {parameters}")
        
        # Format message
        formatted_message = self._format_message(message_template, parameters)
        
        # Output log
        if log_type.lower() == 'debug':
            MaaLog_Debug(formatted_message)
        else:
            MaaLog_Info(formatted_message)
        
        return True

@AgentServer.custom_action("parametric_telegram")
class ParametricTelegramAction(ParametricBaseAction):
    """
    Support reading message template and parameters from custom_action_param and send to Telegram
    """
    
    def __init__(self):
        super().__init__()
        self.notifier = None
    
    def _get_notifier(self):
        """Get Telegram notifier"""
        if self.notifier is None:
            bot_token, chat_id = get_telegram_config()
            if not bot_token or not chat_id:
                MaaLog_Debug("Telegram configuration not set, cannot send message")
                return None
            self.notifier = TelegramNotifier(bot_token, chat_id)
        return self.notifier
    
    def _handle_default_message(self):
        """Handle default message"""
        notifier = self._get_notifier()
        if not notifier:
            return False
        return notifier.send_message("Default Telegram message")
    
    def _handle_string_message(self, message: str):
        """Handle string message"""
        notifier = self._get_notifier()
        if not notifier:
            return False
        return notifier.send_message(message)
    
    def _handle_dict_message(self, param_dict: dict):
        """Handle dictionary parameter message"""
        notifier = self._get_notifier()
        if not notifier:
            return False
        
        message_template = param_dict.get('message', 'Default Telegram message')
        parameters = param_dict.get('parameters', {})
        
        MaaLog_Debug(f"Start processing parametric Telegram message - template: {message_template}, parameters: {parameters}")
        
        # Format message
        formatted_message = self._format_message(message_template, parameters)
        
        # Send to Telegram
        return notifier.send_message(formatted_message)

@AgentServer.custom_action("parametric_wechat")
class ParametricWeChatAction(ParametricBaseAction):
    """
    Support reading message template and parameters from custom_action_param and send to Enterprise WeChat
    """
    
    def __init__(self):
        super().__init__()
        self.notifier = None
    
    def _get_notifier(self):
        """Get Enterprise WeChat notifier"""
        if self.notifier is None:
            webhook_key = get_wechat_config()
            if not webhook_key:
                MaaLog_Debug("Enterprise WeChat configuration not set, cannot send message")
                return None
            self.notifier = WeChatWorkNotifier(webhook_key)
        return self.notifier
    
    def _handle_default_message(self):
        """Handle default message"""
        notifier = self._get_notifier()
        if not notifier:
            return False
        return notifier.send_message("Default Enterprise WeChat message")
    
    def _handle_string_message(self, message: str):
        """Handle string message"""
        notifier = self._get_notifier()
        if not notifier:
            return False
        return notifier.send_message(message)
    
    def _handle_dict_message(self, param_dict: dict):
        """Handle dictionary parameter message"""
        notifier = self._get_notifier()
        if not notifier:
            return False
        
        message_template = param_dict.get('message', 'Default Enterprise WeChat message')
        parameters = param_dict.get('parameters', {})
        msgtype = param_dict.get('msgtype', 'text')  # Support message type setting
        
        MaaLog_Debug(f"Start processing parametric Enterprise WeChat message - template: {message_template}, parameters: {parameters}, type: {msgtype}")
        
        # Format message
        formatted_message = self._format_message(message_template, parameters)
        
        # Send to Enterprise WeChat
        return notifier.send_message(formatted_message, msgtype)

@AgentServer.custom_action("parametric_extnotify")
class ParametricExtNotifyAction(ParametricBaseAction):
    """
    Smart external notification action
    Automatically choose Telegram or Enterprise WeChat to send message based on configuration
    """
    
    def __init__(self):
        super().__init__()
        self.telegram_notifier = None
        self.wechat_notifier = None
    
    def _get_telegram_notifier(self):
        """Get Telegram notifier"""
        if self.telegram_notifier is None:
            bot_token, chat_id = get_telegram_config()
            if bot_token and chat_id:
                self.telegram_notifier = TelegramNotifier(bot_token, chat_id)
        return self.telegram_notifier
    
    def _get_wechat_notifier(self):
        """Get Enterprise WeChat notifier"""
        if self.wechat_notifier is None:
            webhook_key = get_wechat_config()
            if webhook_key:
                self.wechat_notifier = WeChatWorkNotifier(webhook_key)
        return self.wechat_notifier
    
    def _send_message_with_fallback(self, message, msgtype="text", preferred_platform=None):
        """
        Send message with automatic fallback support
        """
        # Get default platform and available platforms
        default_platform = preferred_platform or get_default_ext_notify()
        available_platforms = get_available_notifiers()
        
        MaaLog_Debug(f"Smart notification - default platform: {default_platform}, available platforms: {available_platforms}")
        
        if not available_platforms:
            MaaLog_Debug("Smart notification failed: no available notification platforms")
            return False
        
        # Build try order
        try_order = []
        if default_platform and default_platform in available_platforms:
            try_order.append(default_platform)
        
        # Add other available platforms as alternatives
        for platform in available_platforms:
            if platform not in try_order:
                try_order.append(platform)
        
        MaaLog_Debug(f"Smart notification try order: {try_order}")
        
        # Try sending in order
        for platform in try_order:
            try:
                if platform == 'telegram':
                    notifier = self._get_telegram_notifier()
                    if notifier:
                        MaaLog_Debug(f"Trying to send message via Telegram")
                        if notifier.send_message(message):
                            MaaLog_Debug(f"Smart notification success: sent via Telegram")
                            return True
                        else:
                            MaaLog_Debug(f"Telegram sending failed, trying next platform")
                elif platform == 'wechat':
                    notifier = self._get_wechat_notifier()
                    if notifier:
                        MaaLog_Debug(f"Trying to send message via Enterprise WeChat")
                        if notifier.send_message(message, msgtype):
                            MaaLog_Debug(f"Smart notification success: sent via Enterprise WeChat")
                            return True
                        else:
                            MaaLog_Debug(f"Enterprise WeChat sending failed, trying next platform")
            except Exception as e:
                MaaLog_Debug(f"{platform} sending exception: {e}, trying next platform")
                continue
        
        MaaLog_Debug("Smart notification failed: all platforms unable to send message")
        return False
    
    def _handle_default_message(self):
        """Handle default message"""
        return self._send_message_with_fallback("Default smart notification message")
    
    def _handle_string_message(self, message: str):
        """Handle string message"""
        return self._send_message_with_fallback(message)
    
    def _handle_dict_message(self, param_dict: dict):
        """Handle dictionary parameter message"""
        message_template = param_dict.get('message', 'Default smart notification message')
        parameters = param_dict.get('parameters', {})
        msgtype = param_dict.get('msgtype', 'text')
        preferred_platform = param_dict.get('platform', None)
        
        MaaLog_Debug(f"Start processing parametric smart notification message - template: {message_template}, parameters: {parameters}, type: {msgtype}, preferred platform: {preferred_platform}")
        
        # Format message
        formatted_message = self._format_message(message_template, parameters)
        
        # Send message
        return self._send_message_with_fallback(formatted_message, msgtype, preferred_platform)

##########################################################################################################################################################################################
################################################################################ Part II : Implementation ################################################################################
##########################################################################################################################################################################################

def MaaLog_Debug(message):
    """Debug log output"""
    if Enable_MaaLog_Debug:
        print(f"[DEBUG] {message}")

def MaaLog_Info(message):
    """Info log output"""
    if Enable_MaaLog_Info:
        print(f"[INFO] {message}")

def set_debug_log(enabled):
    """Set debug log switch"""
    global Enable_MaaLog_Debug
    Enable_MaaLog_Debug = 1 if enabled else 0

def set_info_log(enabled):
    """Set info log switch"""
    global Enable_MaaLog_Info
    Enable_MaaLog_Info = 1 if enabled else 0

def get_Task_Counter():
    """Get current task run count"""
    global Task_Counter
    return Task_Counter

def reset_Task_Counter():
    """Reset task run count"""
    global Task_Counter
    Task_Counter = 0