import sys
import os
import traceback
import time
import uuid

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
    from action import input, log
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
    
    from config import load_config
    load_config(config_path)
    print("Configuration file loading completed")
    
except Exception as e:
    print(f"Configuration file loading failed: {e}")
    traceback.print_exc()
    sys.exit(1)

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

        print("Starting to launch AgentServer...")
        AgentServer.start_up(socket_id)
        print("AgentServer started successfully")
        
        # Wait for AgentServer to fully start
        print("Waiting for AgentServer to fully start...")
        time.sleep(2)
        print("AgentServer startup wait completed")
        print("Starting to wait for connections...")
        
        # AgentServer.join() will block until connection ends
        AgentServer.join()
        print("AgentServer connection ended")
        
        # Clean up resources
        AgentServer.shut_down()
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