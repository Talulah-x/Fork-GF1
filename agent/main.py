import sys
import os
import traceback
import time
import uuid
import threading

def get_executable_dir():
    """Get the directory where the executable is located"""
    if getattr(sys, 'frozen', False):
        # If it's a packaged exe
        return os.path.dirname(sys.executable)
    else:
        # If it's development environment
        return os.path.dirname(os.path.abspath(__file__))

def get_project_root():
    """Get the project root directory"""
    current_dir = get_executable_dir()
    
    if getattr(sys, 'frozen', False):
        # Packaged exe environment: from PROJECT_DIR/agent/dist/ back to PROJECT_DIR/
        return os.path.dirname(os.path.dirname(current_dir))
    else:
        # Development environment: from PROJECT_DIR/agent/ back to PROJECT_DIR/
        return os.path.dirname(current_dir)

def setup_dll_path():
    """Setup DLL path"""
    current_dir = get_executable_dir()
    project_root = get_project_root()
    
    print(f"Current directory: {current_dir}")
    print(f"Project root directory: {project_root}")
    print(f"Runtime environment: {'Packaged exe' if getattr(sys, 'frozen', False) else 'Development environment'}")
    
    # DLL is in project root directory
    dll_dir = project_root
    
    # Check if key DLL files exist
    key_dlls = [
        "MaaFramework.dll",
        "MaaAgentServer.dll", 
        "MaaToolkit.dll"
    ]
    
    dll_exists = True
    for dll_name in key_dlls:
        dll_path = os.path.join(dll_dir, dll_name)
        if os.path.exists(dll_path):
            print(f"Found {dll_name}: {dll_path}")
        else:
            print(f"Not found {dll_name}: {dll_path}")
            dll_exists = False
    
    if not dll_exists:
        print("Key DLL files are missing, program cannot run")
        sys.exit(1)
    
    # Set MAAFW_BINARY_PATH environment variable
    os.environ["MAAFW_BINARY_PATH"] = dll_dir
    print(f"Set MAAFW_BINARY_PATH: {dll_dir}")
    
    # Add DLL directory to the front of PATH
    old_path = os.environ.get("PATH", "")
    new_path = dll_dir + os.pathsep + old_path
    os.environ["PATH"] = new_path
    print(f"Added DLL directory to PATH: {dll_dir}")
    
    # Set other environment variables
    os.environ["MAA_LIBRARY_PATH"] = dll_dir
    
    return dll_dir, project_root

def generate_socket_id():
    """Generate a unique socket_id"""
    return f"maa_agent_{uuid.uuid4().hex[:8]}"

# Setup DLL path and environment variables before importing MaaFramework
print("Starting DLL environment setup...")
dll_dir, project_root = setup_dll_path()
print("DLL environment setup completed")

# Now import maa modules
try:
    print("Starting to import MaaFramework modules...")
    from maa.agent.agent_server import AgentServer
    from maa.toolkit import Toolkit
    print("MaaFramework modules imported successfully")
except Exception as e:
    print(f"MaaFramework module import failed: {e}")
    print("Detailed error information:")
    traceback.print_exc()
    
    print(f"\nDebug information:")
    print(f"MAAFW_BINARY_PATH: {os.environ.get('MAAFW_BINARY_PATH', 'Not set')}")
    print(f"First few PATH directories: {os.environ.get('PATH', '')[:200]}...")
    sys.exit(1)

# Import custom modules
try:
    print("Starting to import custom modules...")
    import my_reco
    import action
    from action import get_global_watchdog
    print("Custom modules imported successfully")
    
except Exception as e:
    print(f"Custom module import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Load configuration file
try:
    print("Starting to load configuration file...")
    
    # Fix configuration file path
    if getattr(sys, 'frozen', False):
        # Packaged environment: config file is in agent subdirectory of project root
        config_path = os.path.join(project_root, "agent", "agent.conf")
    else:
        # Development environment: config file is in current directory
        config_path = os.path.join(get_executable_dir(), "agent.conf")
    
    print(f"Configuration file path: {config_path}")
    
    from utils import load_config, get_watchdog_interval, is_watchdog_interval_configured
    load_config(config_path)
    print("Configuration file loading completed")
    
    # Get watchdog interval from configuration
    watchdog_interval = get_watchdog_interval()
    interval_from_config = is_watchdog_interval_configured()
    
    print(f"Watchdog check interval: {watchdog_interval} seconds ({'from config file' if interval_from_config else 'using default'})")
    
except Exception as e:
    print(f"Configuration file loading failed: {e}")
    traceback.print_exc()
    # Set default watchdog interval if config loading fails
    watchdog_interval = 5.0
    print(f"Using fallback watchdog interval: {watchdog_interval} seconds")
    # Don't exit here, continue with defaults
    # sys.exit(1)

class CustomAgentServer:
    """
    Custom AgentServer wrapper with watchdog monitoring
    """
    
    def __init__(self, watchdog_check_interval=None):
        # Use provided interval or get from global config
        if watchdog_check_interval is not None:
            self._watchdog_check_interval = float(watchdog_check_interval)
        else:
            try:
                from utils import get_watchdog_interval
                self._watchdog_check_interval = get_watchdog_interval()
            except:
                # Fallback if config module is not available
                self._watchdog_check_interval = 5.0
        
        print(f"CustomAgentServer initialized with watchdog check interval: {self._watchdog_check_interval} seconds")
        
        self._watchdog_thread = None
        self._stop_event = threading.Event()
        self._watchdog = get_global_watchdog()
    
    def _watchdog_monitor_loop(self):
        """
        Watchdog monitoring loop running in separate thread
        """
        print(f"Watchdog monitor thread started (check interval: {self._watchdog_check_interval}s)")
        
        while not self._stop_event.wait(self._watchdog_check_interval):
            try:
                if self._watchdog.poll():
                    print("Watchdog timeout detected, sending notification...")
                    self._watchdog.notify()
                    # Continue monitoring even after timeout
                else:
                    # Watchdog is healthy, no action needed
                    pass
            except Exception as e:
                print(f"Watchdog monitor exception: {e}")
                traceback.print_exc()
        
        print("Watchdog monitor thread stopped")
    
    def start_up(self, socket_id):
        """Start AgentServer with watchdog monitoring"""
        # Start original AgentServer
        print("Starting to launch AgentServer...")
        AgentServer.start_up(socket_id)
        print("AgentServer started successfully")
        
        # Start watchdog monitoring thread
        self._stop_event.clear()
        self._watchdog_thread = threading.Thread(
            target=self._watchdog_monitor_loop,
            daemon=True,
            name="WatchdogMonitor"
        )
        self._watchdog_thread.start()
        print(f"Watchdog monitor thread started with {self._watchdog_check_interval}s interval")
    
    def join(self):
        """Wait for AgentServer to complete"""
        # This will block until connection ends
        AgentServer.join()
    
    def shut_down(self):
        """Shutdown AgentServer and stop watchdog monitoring"""
        # Stop watchdog monitoring
        if self._watchdog_thread and self._watchdog_thread.is_alive():
            print("Stopping watchdog monitor thread...")
            self._stop_event.set()
            self._watchdog_thread.join(timeout=10)
            if self._watchdog_thread.is_alive():
                print("Warning: Watchdog monitor thread did not stop gracefully")
            else:
                print("Watchdog monitor thread stopped")
        
        # Shutdown original AgentServer
        AgentServer.shut_down()
    
    def set_watchdog_check_interval(self, interval):
        """Set watchdog check interval (requires restart to take effect)"""
        try:
            interval = float(interval)
            if interval > 0:
                self._watchdog_check_interval = interval
                print(f"Watchdog check interval updated to: {interval} seconds (restart required)")
                return True
            else:
                print(f"Invalid watchdog interval: {interval}, must be positive")
                return False
        except (ValueError, TypeError):
            print(f"Invalid watchdog interval format: {interval}")
            return False
    
    def get_watchdog_check_interval(self):
        """Get current watchdog check interval"""
        return self._watchdog_check_interval
    
    # Expose other AgentServer methods if needed
    @staticmethod
    def custom_action(name):
        """Decorator for custom actions"""
        return AgentServer.custom_action(name)

def main():
    
    try:
        print("Starting to initialize MaaFramework...")
        Toolkit.init_option(dll_dir)
        print("MaaFramework initialization completed")

        # Handle socket_id parameter
        print(f"Command line arguments: {sys.argv}")
        
        if len(sys.argv) >= 2:
            # If parameter is provided, use the first parameter as socket_id
            socket_id = sys.argv[1]
            print(f"Using socket_id provided from command line: {socket_id}")
        else:
            # If no parameter is provided, automatically generate a socket_id
            socket_id = generate_socket_id()
            print(f"Auto-generated socket_id: {socket_id}")
        
        print(f"Final socket_id to use: {socket_id}")

        # Create custom agent server with watchdog support
        # Pass the watchdog interval from configuration
        custom_agent_server = CustomAgentServer(watchdog_interval)
        
        # Start up the server
        custom_agent_server.start_up(socket_id)
        
        # Wait for AgentServer to fully start
        print("Waiting for AgentServer to fully start...")
        time.sleep(2)
        print("AgentServer startup wait completed")
        print("Starting to wait for connections...")
        
        # AgentServer.join() will block until connection ends
        custom_agent_server.join()
        print("AgentServer connection ended")
        
        # Clean up resources
        custom_agent_server.shut_down()
        print("All services shutdown completed")

    except Exception as e:
        print(f"Service startup failed: {e}")
        print("Detailed error information:")
        traceback.print_exc()
        
        # Output debug information
        print(f"\nDebug information:")
        print(f"Current working directory: {os.getcwd()}")
        print(f"MAAFW_BINARY_PATH: {os.environ.get('MAAFW_BINARY_PATH', 'Not set')}")
        print(f"Command line arguments: {sys.argv}")
        
        try:
            AgentServer.shut_down()
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()