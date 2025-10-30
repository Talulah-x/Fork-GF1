"""
Utils package initialization
Provides unified access to configuration and common utilities
"""

from .config import (
    app_config,
    load_config,
    get_telegram_config,
    get_wechat_config, 
    get_default_ext_notify,
    get_available_notifiers,
    get_watchdog_interval,
    set_telegram_config,
    set_wechat_config,
    set_default_ext_notify,
    set_watchdog_interval,
    is_telegram_configured,
    is_wechat_configured,
    is_watchdog_interval_configured
)

__all__ = [
    'app_config',
    'load_config',
    'get_telegram_config',
    'get_wechat_config',
    'get_default_ext_notify', 
    'get_available_notifiers',
    'get_watchdog_interval',
    'set_telegram_config',
    'set_wechat_config',
    'set_default_ext_notify',
    'set_watchdog_interval',
    'is_telegram_configured',
    'is_wechat_configured',
    'is_watchdog_interval_configured'
]