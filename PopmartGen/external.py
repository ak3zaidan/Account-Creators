import subprocess
import time

while True:
    try:
        print("Running: go run main.go")

        subprocess.run(["go", "run", "main.go"])

        time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped by user.")
        break
    except Exception as e:
        print(f"Error occurred: {e}")
        time.sleep(2)
