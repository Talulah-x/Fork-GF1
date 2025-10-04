# Mouse wheel automation script for Girls' Frontline
# Configurable parameters
param(
    [int]$ScrollCount = 100,           # Number of scroll operations
    [string]$Direction = "down"        # Scroll direction: "up" or "down"
)

try {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    
    # Define Windows API functions
    Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public class MouseWheelHelper {
    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
    
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
    
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    
    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);
    
    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
    
    public const uint MOUSEEVENTF_WHEEL = 0x0800;
    
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT {
        public int Left, Top, Right, Bottom;
    }
}
"@

    # Validate direction parameter
    if ($Direction -notin @("up", "down")) {
        Write-Host "Error: Direction must be 'up' or 'down'"
        exit 1
    }
    
    # Set wheel delta based on direction
    # For down direction, use uint representation of negative value
    $wheelDelta = if ($Direction -eq "up") { 
        [uint32]120 
    } else { 
        [uint32]([uint32]::MaxValue - 120 + 1)  # Equivalent to -120 in uint32
    }
    
    Write-Host "Searching for game window..."
    Write-Host "Wheel delta: $wheelDelta (Direction: $Direction)"
    
    # Method 1: Find by window title
    $gameWindowTitles = @("少女前线", "Girls' Frontline", "GirlsFrontline")
    $gameWindow = [System.IntPtr]::Zero
    $foundTitle = ""
    
    foreach ($title in $gameWindowTitles) {
        $window = [MouseWheelHelper]::FindWindow($null, $title)
        if ($window -ne [System.IntPtr]::Zero) {
            $gameWindow = $window
            $foundTitle = $title
            Write-Host "Found window: $title"
            break
        }
    }
    
    # Method 2: Find by process name if method 1 failed
    if ($gameWindow -eq [System.IntPtr]::Zero) {
        $processes = Get-Process -Name "GrilsFrontLine" -ErrorAction SilentlyContinue
        if ($processes) {
            foreach ($process in $processes) {
                if ($process.MainWindowHandle -ne [System.IntPtr]::Zero) {
                    $gameWindow = $process.MainWindowHandle
                    $foundTitle = $process.MainWindowTitle
                    Write-Host "Found via process: $($process.MainWindowTitle)"
                    break
                }
            }
        }
    }
    
    # Exit if no game window found
    if ($gameWindow -eq [System.IntPtr]::Zero) {
        Write-Host "Error: Game window not found"
        exit 1
    }
    
    # Verify window visibility
    $isVisible = [MouseWheelHelper]::IsWindowVisible($gameWindow)
    if (-not $isVisible) {
        Write-Host "Warning: Game window is not visible"
    }
    
    # Get window position and calculate center
    $rect = New-Object MouseWheelHelper+RECT
    $rectResult = [MouseWheelHelper]::GetWindowRect($gameWindow, [ref]$rect)
    if ($rectResult) {
        $centerX = ($rect.Left + $rect.Right) / 2
        $centerY = ($rect.Top + $rect.Bottom) / 2
        Write-Host "Window center: ($centerX, $centerY)"
    }
    
    # Activate game window
    Write-Host "Activating game window..."
    $activateResult = [MouseWheelHelper]::SetForegroundWindow($gameWindow)
    if (-not $activateResult) {
        Write-Host "Warning: Failed to activate window"
    }
    Start-Sleep -Milliseconds 500
    
    # Verify activation
    $currentForeground = [MouseWheelHelper]::GetForegroundWindow()
    $isActivated = ($currentForeground -eq $gameWindow)
    if (-not $isActivated) {
        Write-Host "Warning: Window activation failed, continuing anyway..."
    }
    
    # Set mouse position to window center
    [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($centerX, $centerY)
    Start-Sleep -Milliseconds 200
    
    # Perform mouse wheel operations
    Write-Host "Executing $ScrollCount scroll operations ($Direction)..."
    for ($i = 0; $i -lt $ScrollCount; $i++) {
        [MouseWheelHelper]::mouse_event([MouseWheelHelper]::MOUSEEVENTF_WHEEL, 0, 0, $wheelDelta, [System.UIntPtr]::Zero)
        Write-Host "Scroll $($i + 1)/$ScrollCount completed"
        Start-Sleep -Milliseconds 1
    }
    
    Write-Host "All operations completed successfully"
    
}
catch {
    Write-Host "Error: $($_.Exception.Message)"
    exit 1
}