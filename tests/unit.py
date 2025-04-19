import subprocess
import time

cmd = ['arecord', '-D', 'default', '-f', 'S16_LE', '-c', '1', '-r', '16000', '-t', 'raw']
process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

try:
    for _ in range(2):  # Read 100 chunks
        raw_data = process.stdout.read(2048)
        energy = sum(abs(b) for b in raw_data) / len(raw_data)
        print(f"Energy: {energy}")
        time.sleep(0.1)
finally:
    process.terminate()