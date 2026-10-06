import subprocess
import os
import signal

class DemoController:
    def __init__(self):
        self.demo_process = None
        
    def start_demo(self, anomaly_type):
        self.stop_demo() # Ensure any existing demo is stopped
        script_path = os.path.join(os.path.dirname(__file__), 'demo_worker.py')
        
        # Start as a subprocess
        # We pass python.exe to run it
        # On Windows, psutil doesn't always show the script name in proc.name(), 
        # it shows python.exe. We can identify it via command line args in app.py if needed,
        # or we just let it run.
        self.demo_process = subprocess.Popen(
            ["python", script_path, "--type", anomaly_type, "--duration", "300"]
        )
        return self.demo_process.pid
        
    def stop_demo(self):
        if self.demo_process and self.demo_process.poll() is None:
            try:
                # Windows
                if os.name == 'nt':
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.demo_process.pid)])
                else:
                    os.kill(self.demo_process.pid, signal.SIGTERM)
            except Exception as e:
                print(f"Error stopping demo: {e}")
            self.demo_process = None
