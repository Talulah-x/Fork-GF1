# Std Lib
import time
import ctypes
import sys
import os
import traceback
import json
import re

# Win32
import win32con
import win32gui
import win32process
import win32api
import win32ui
from ctypes import windll, wintypes, byref, sizeof

# CV
from PIL import Image, ImageGrab
import numpy as np

# MaaFramework
from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

#################### Global ####################

# Default Counter
Task_Counter = 0

#################### Log Control ####################

Enable_MaaLog_Debug = 0
Enable_MaaLog_Info = 0