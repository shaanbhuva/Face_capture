import subprocess
import time

if __name__ == "__main__":
    
    flask_process = subprocess.Popen(['python', 'app.py'])
    time.sleep(3)
    subprocess.run(['python', 'main.py'])
    flask_process.terminate()