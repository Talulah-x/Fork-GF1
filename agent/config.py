"""
配置管理模块
负责加载和管理应用程序配置
"""
import os

class Config:
    """配置管理类"""
    
    def __init__(self):
        self.bot_token = None
        self.chat_id = None
        self.loaded = False
    
    def load_config(self, config_path=None):
        """
        加载配置文件
        """
        if config_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, "agent.conf")
        
        print(f"尝试加载配置文件: {config_path}")
        
        if not os.path.exists(config_path):
            print(f"配置文件不存在: {config_path}")
            return False
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == 'Bot_Token':
                            self.bot_token = value
                            print(f"已加载 Bot_Token: {self.bot_token[:10]}...")
                        elif key == 'Chat_ID':
                            self.chat_id = value
                            print(f"已加载 Chat_ID: {self.chat_id}")
            
            if self.bot_token and self.chat_id:
                print("Telegram配置加载成功")
                self.loaded = True
                return True
            else:
                print("Telegram配置不完整")
                self.loaded = False
                return False
                
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self.loaded = False
            return False
    
    def get_telegram_config(self):
        """
        获取Telegram配置
        """
        return self.bot_token, self.chat_id
    
    def set_telegram_config(self, bot_token, chat_id):
        """
        手动设置Telegram配置
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.loaded = True
        print(f"已手动设置Telegram配置")
    
    def is_telegram_configured(self):
        """
        检查Telegram是否已配置
        """
        return self.loaded and self.bot_token and self.chat_id

# 全局配置实例
app_config = Config()

def load_config(config_path=None):
    """加载配置文件"""
    return app_config.load_config(config_path)

def get_telegram_config():
    """获取Telegram配置"""
    return app_config.get_telegram_config()

def set_telegram_config(bot_token, chat_id):
    """手动设置Telegram配置"""
    return app_config.set_telegram_config(bot_token, chat_id)

def is_telegram_configured():
    """检查Telegram是否已配置"""
    return app_config.is_telegram_configured()