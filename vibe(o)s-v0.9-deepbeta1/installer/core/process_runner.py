import subprocess
import threading

class ProcessRunner:
    """
    Runs shell commands asynchronously to prevent freezing the CustomTkinter GUI.
    Captures stdout/stderr and sends it to a callback function in real-time.
    """
    def __init__(self, output_callback, completion_callback):
        self.output_callback = output_callback
        self.completion_callback = completion_callback

    def run(self, command):
        thread = threading.Thread(target=self._run_process, args=(command,))
        thread.daemon = True
        thread.start()

    def _run_process(self, command):
        try:
            process = subprocess.Popen(
                command, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True,
                bufsize=1
            )
            
            # Read output line by line as it is generated
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.output_callback(line.strip())
            
            process.stdout.close()
            return_code = process.wait()
            self.completion_callback(return_code)
            
        except Exception as e:
            self.output_callback(f"[ERROR] Failed to execute process: {str(e)}")
            self.completion_callback(1)
