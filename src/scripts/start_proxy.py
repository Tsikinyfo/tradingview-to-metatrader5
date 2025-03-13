import asyncio
import logging
import os
import signal
import subprocess
import sys
from pathlib import Path

import psutil
from dotenv import load_dotenv


def kill_process_on_port(port):
    """Kill process running on specified port."""
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    # Don't print for System Idle Process
                    if proc.pid != 0:  # System Idle Process has PID 0
                        print(f"Stopping process on port {port}: {proc.name()} (PID: {proc.pid})")
                    proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def kill_mitm_processes():
    """Kill any existing mitmproxy processes."""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'mitm' in proc.name().lower():
                print(f"Stopping process: {proc.name()} (PID: {proc.pid})")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def get_project_root():
    """Get the project root directory."""
    return str(Path(__file__).resolve().parent.parent.parent)

def setup_environment():
    """Setup the Python environment."""
    project_root = get_project_root()
    os.environ['PYTHONPATH'] = project_root
    return project_root

def cleanup():
    """Cleanup on exit."""
    kill_mitm_processes()
    kill_process_on_port(8080)

def signal_handler(signum, frame):
    """Handle termination signals."""
    print("\n⛔ Shutdown requested...")
    cleanup()
    sys.exit(0)

def check_environment():
    """Check if all required environment variables are set."""
    load_dotenv()
    required_vars = ['TV_BROKER_URL', 'TV_ACCOUNT_ID', 'MT5_DEFAULT_SUFFIX']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print("\n❌ Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        return False
    return True


def run_proxy():
    """Run the proxy server with minimal output."""
    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Initial cleanup and port check (do this before clearing screen)
        print("Killing previous processes on port :8080")
        cleanup()

        # Clear screen only after cleanup
        os.system('cls' if os.name == 'nt' else 'clear')

        # Setup environment
        project_root = setup_environment()

        # Print banner
        print("\nTradingView Proxy Server")
        print("========================")
        print("Starting proxy server...")
        print("Press Ctrl+C to stop\n")

        # Configure logging to handle connection resets gracefully
        logging.getLogger('asyncio').setLevel(logging.CRITICAL)
        
        # Configure mitmproxy logging
        logging.getLogger('mitmproxy.proxy.protocol').setLevel(logging.WARNING)
        
        # Set up custom error handler for asyncio
        def custom_exception_handler(loop, context):
            exception = context.get('exception')
            if isinstance(exception, ConnectionResetError) and getattr(exception, 'winerror', None) == 10054:
                # Silently ignore connection resets during internet outages
                return
            if 'exception' not in context:
                loop.default_exception_handler(context)
                return
            
            # Log other errors appropriately
            logger = logging.getLogger('ProxyServer')
            if isinstance(exception, (ConnectionResetError, ConnectionError)):
                logger.debug(f"Connection error: {exception}")
            else:
                logger.error(f"Unhandled error: {exception}")

        # Get event loop using the new recommended way
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        loop.set_exception_handler(custom_exception_handler)

        # Construct mitmdump command
        cmd = [
            "mitmdump",
            "--quiet",
            "--listen-host", "127.0.0.1",
            "--listen-port", "8080",
            "--mode", "regular",
            "--ssl-insecure",
            "--set", "console_output_level=error",
            "--set", "flow_detail=0",
            "--set", "connection_strategy=lazy",  # Better handling of connection issues
            "-s", str(Path(project_root) / "src" / "main.py"),
            "~u orders\\?locale=\\w+&requestId=\\w+ | ~u executions\\?locale=\\w+&instrument=\\w+"
        ]

        # Run mitmdump
        subprocess.run(cmd)

    except KeyboardInterrupt:
        print("\n⛔ Shutdown requested...")
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
    finally:
        cleanup()
        print("\nProxy server stopped.")

if __name__ == "__main__":
    run_proxy()