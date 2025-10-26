"""
Action package initialization
Provides unified access to all action module functionalities
"""

# Import all submodules
from . import include
from . import log
from . import input

# Import commonly used functions and classes for convenient access
from .log import MaaLog_Debug, MaaLog_Info
from .input import (
    win32_mouse_left_down, 
    win32_mouse_left_up, 
    find_game_window, 
    convert_maa_coordinates
)

# Import global variables and configuration from include
from .include import (
    Task_Counter,
    Enable_MaaLog_Debug,
    Enable_MaaLog_Info
)

# Define what gets exported when using "from action import *"
__all__ = [
    # Submodules
    'include',
    'log', 
    'input',
    
    # Logging functions
    'MaaLog_Debug',
    'MaaLog_Info',
    
    # Input functions
    'win32_mouse_left_down',
    'win32_mouse_left_up', 
    'find_game_window',
    'convert_maa_coordinates',
    
    # Global variables
    'Task_Counter',
    'Enable_MaaLog_Debug',
    'Enable_MaaLog_Info'
]

# Package metadata
__version__ = '1.0.0'
__author__ = 'MaaGF1 Team'
__description__ = 'Action module for MaaFramework agent'