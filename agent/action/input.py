from .include import *
from .log import MaaLog_Debug, MaaLog_Info

#######################################################################################################################################################################################
################################################################################ Part I : Registration ################################################################################
#######################################################################################################################################################################################

@AgentServer.custom_action("custom_mouse_left_down")
class CustomMouseLeftDownAction(CustomAction):
    """
    Custom mouse left button down action
    Implemented using Win32 API
    """
    
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        MaaLog_Debug("custom_mouse_left_down action started")
        
        try:
            MaaLog_Debug("Executing mouse left button down operation")
            
            # Execute mouse left button down using Win32 API
            result = win32_mouse_left_down()
            
            if result:
                MaaLog_Debug("Mouse left button down operation executed successfully")
                MaaLog_Debug("==========================================\n")
                return CustomAction.RunResult(success=True)
            else:
                MaaLog_Debug("Mouse left button down operation failed")
                MaaLog_Debug("==========================================\n")
                return CustomAction.RunResult(success=False)
                
        except Exception as e:
            MaaLog_Debug(f"Exception occurred during custom_mouse_left_down action execution: {e}")
            traceback.print_exc()
            MaaLog_Debug("==========================================\n")
            return CustomAction.RunResult(success=False)

@AgentServer.custom_action("custom_mouse_left_up")
class CustomMouseLeftUpAction(CustomAction):
    """
    Custom mouse left button up action
    Implemented using Win32 API
    """
    
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        MaaLog_Debug("custom_mouse_left_up action started")
        
        try:
            MaaLog_Debug("Executing mouse left button up operation")
            
            # Execute mouse left button up using Win32 API
            result = win32_mouse_left_up()
            
            if result:
                MaaLog_Debug("Mouse left button up operation executed successfully")
                MaaLog_Debug("==========================================\n")
                return CustomAction.RunResult(success=True)
            else:
                MaaLog_Debug("Mouse left button up operation failed")
                MaaLog_Debug("==========================================\n")
                return CustomAction.RunResult(success=False)
                
        except Exception as e:
            MaaLog_Debug(f"Exception occurred during custom_mouse_left_up action execution: {e}")
            traceback.print_exc()
            MaaLog_Debug("==========================================\n")
            return CustomAction.RunResult(success=False)

##########################################################################################################################################################################################
################################################################################ Part II : Implementation ################################################################################
##########################################################################################################################################################################################

def find_game_window():
    """Find Girls' Frontline game window"""
    try:
        hwnd = win32gui.FindWindow(None, "Girls' Frontline")
        if hwnd == 0:
            # Try fuzzy matching
            MaaLog_Debug("Failed to match 'Girls' Frontline' window exactly, trying fuzzy matching...")
            all_windows = []
            win32gui.EnumWindows(lambda h, param: param.append((h, win32gui.GetWindowText(h))), all_windows)
            
            MaaLog_Debug(f"Found window list:")
            for h, title in all_windows:
                if len(title) > 0:  # Only show windows with titles
                    MaaLog_Debug(f"  - Window handle: {h}, title: '{title}'")
                    
                    if "Girls' Frontline" in title or "Mabinogi" in title:
                        hwnd = h
                        MaaLog_Debug(f"  --> Matched Girls' Frontline window!")
                        break
        
        if hwnd != 0:
            # Check if window is visible
            if win32gui.IsWindowVisible(hwnd):
                # Get window position and size
                rect = win32gui.GetWindowRect(hwnd)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                
                # Get client area size
                client_rect = win32gui.GetClientRect(hwnd)
                client_width = client_rect[2]
                client_height = client_rect[3]
                
                MaaLog_Debug(f"Found Girls' Frontline window, handle: {hwnd}")
                MaaLog_Debug(f"Window position: ({rect[0]}, {rect[1]}, {rect[2]}, {rect[3]})")
                MaaLog_Debug(f"Window size: {width}x{height}")
                MaaLog_Debug(f"Client area size: {client_width}x{client_height}")
                
                return hwnd
            else:
                MaaLog_Debug(f"Warning: Found Girls' Frontline window (handle: {hwnd}) but window is not visible")
        
        MaaLog_Debug("Warning: Girls' Frontline window not found, will try to find other possible game windows")
        
        # Try to find any large window that might be a game window
        all_windows = []
        win32gui.EnumWindows(lambda h, param: param.append((h, win32gui.GetWindowText(h))), all_windows)
        
        for h, title in all_windows:
            if not title:  # Skip windows without titles
                continue
                
            # Check if window is visible and has appropriate size
            if win32gui.IsWindowVisible(h):
                rect = win32gui.GetWindowRect(h)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                
                # Game windows are usually large
                if width > 400 and height > 300:
                    MaaLog_Debug(f"Found possible game window: handle={h}, title='{title}', size={width}x{height}")
                    
                    # Ask if this window should be used
                    hwnd = h
                    MaaLog_Debug(f"Will use window: handle={hwnd}, title='{title}'")
                    return hwnd
        
        # If still can't find a suitable window, use current active window
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        
        MaaLog_Debug(f"No suitable window found, will use current active window:")
        MaaLog_Debug(f"handle={hwnd}, title='{window_title}', size={width}x{height}")
        return hwnd
            
    except Exception as e:
        MaaLog_Debug(f"Error while finding game window: {e}")
        traceback.print_exc()
        
        # Use current active window when error occurs
        try:
            hwnd = win32gui.GetForegroundWindow()
            MaaLog_Debug(f"Due to error, using current active window, handle: {hwnd}")
            return hwnd
        except:
            MaaLog_Debug("Cannot get any window, returning 0")
            return 0

def convert_maa_coordinates(x, y, hwnd=None, maa_width=1280, maa_height=720, x_correction=1):
    """Convert MAA coordinates to screen absolute coordinates in game window
    
    Parameters:
        x, y: Relative coordinates in MAA (based on 720P scaled coordinates)
        hwnd: Game window handle, if None will try to find
        maa_width: Width used by MAA, default 1280
        maa_height: Height used by MAA, default 720
        x_correction: Additional correction factor for x-axis, default 1
        
    Returns:
        tuple: (screen_x, screen_y) Screen absolute coordinates
    """
    try:
        # If no window handle provided, find game window
        if hwnd is None:
            hwnd = find_game_window()
            if hwnd == 0:
                MaaLog_Debug("Error: Cannot find game window")
                return x, y  # If window not found, return original coordinates
        
        # Get client area position on screen
        client_point = wintypes.POINT(0, 0)
        windll.user32.ClientToScreen(hwnd, byref(client_point))
        client_x, client_y = client_point.x, client_point.y
        
        # Get client area size
        client_rect = win32gui.GetClientRect(hwnd)
        client_width, client_height = client_rect[2], client_rect[3]
        
        MaaLog_Debug(f"Client area top-left screen coordinates: ({client_x}, {client_y})")
        MaaLog_Debug(f"Client area actual size: {client_width}x{client_height}")
        MaaLog_Debug(f"MAA resolution: {maa_width}x{maa_height}")
        
        # Calculate scaling ratio
        scale_x = client_width / maa_width
        scale_y = client_height / maa_height
        
        # Apply x-axis correction factor
        corrected_scale_x = scale_x * x_correction
        
        MaaLog_Debug(f"Base scaling ratio: X-axis={scale_x:.3f}, Y-axis={scale_y:.3f}")
        MaaLog_Debug(f"X-axis correction factor: {x_correction}")
        MaaLog_Debug(f"Corrected scaling ratio: X-axis={corrected_scale_x:.3f}, Y-axis={scale_y:.3f}")
        
        # Convert coordinates based on scaling ratio
        real_x = int(x * corrected_scale_x)
        real_y = int(y * scale_y)
        MaaLog_Debug(f"MAA coordinates({x}, {y}) -> Client area relative coordinates({real_x}, {real_y})")
        
        # Calculate absolute coordinates
        screen_x = client_x + real_x
        screen_y = client_y + real_y
        MaaLog_Debug(f"Client area relative coordinates({real_x}, {real_y}) -> Screen absolute coordinates({screen_x}, {screen_y})")
        
        return screen_x, screen_y
    
    except Exception as e:
        MaaLog_Debug(f"Coordinate conversion failed: {e}")
        traceback.print_exc()
        return x, y  # Return original coordinates when error occurs

def win32_mouse_left_down():
    """
    Execute mouse left button down operation using Win32 API
    Uses current mouse position
    
    Returns:
        bool: Whether successful
    """
    try:
        MaaLog_Debug("Executing Win32 mouse left button down")
        
        # Get current mouse position
        current_pos = win32api.GetCursorPos()
        screen_x, screen_y = current_pos[0], current_pos[1]
        MaaLog_Debug(f"Current mouse position: ({screen_x}, {screen_y})")
        
        # Ensure target window gets focus
        hwnd = find_game_window()
        if hwnd == 0:
            MaaLog_Debug("Error: Cannot find game window")
            return False
            
        # Activate window and wait
        MaaLog_Debug(f"Activating window, handle: {hwnd}")
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.2)
        
        # Verify if window is activated
        current_hwnd = win32gui.GetForegroundWindow()
        if current_hwnd != hwnd:
            MaaLog_Debug(f"Warning: Window activation may have failed. Expected: {hwnd}, Actual: {current_hwnd}")
        
        # Send mouse left button down event using mouse_event
        MaaLog_Debug(f"Sending mouse left button down event at position ({screen_x}, {screen_y})")
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        
        MaaLog_Debug("Mouse left button down sent successfully")
        return True
        
    except Exception as e:
        MaaLog_Debug(f"Win32 mouse left button down operation failed: {e}")
        traceback.print_exc()
        return False

def win32_mouse_left_up():
    """
    Execute mouse left button up operation using Win32 API
    Uses current mouse position
    
    Returns:
        bool: Whether successful
    """
    try:
        MaaLog_Debug("Executing Win32 mouse left button up")
        
        # Get current mouse position
        current_pos = win32api.GetCursorPos()
        screen_x, screen_y = current_pos[0], current_pos[1]
        MaaLog_Debug(f"Current mouse position: ({screen_x}, {screen_y})")
        
        # Ensure target window gets focus
        hwnd = find_game_window()
        if hwnd == 0:
            MaaLog_Debug("Error: Cannot find game window")
            return False
            
        # Activate window and wait
        MaaLog_Debug(f"Activating window, handle: {hwnd}")
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.2)
        
        # Verify if window is activated
        current_hwnd = win32gui.GetForegroundWindow()
        if current_hwnd != hwnd:
            MaaLog_Debug(f"Warning: Window activation may have failed. Expected: {hwnd}, Actual: {current_hwnd}")
        
        # Send mouse left button up event using mouse_event
        MaaLog_Debug(f"Sending mouse left button up event at position ({screen_x}, {screen_y})")
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        
        MaaLog_Debug("Mouse left button up sent successfully")
        return True
        
    except Exception as e:
        MaaLog_Debug(f"Win32 mouse left button up operation failed: {e}")
        traceback.print_exc()
        return False