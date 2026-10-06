import time
import math
import sys
import threading
import argparse

def cpu_anomaly(duration):
    print(f"Starting CPU anomaly for {duration} seconds...")
    start_time = time.time()
    while time.time() - start_time < duration:
        # Busy wait to spike CPU
        _ = [math.sqrt(i) for i in range(10000)]
        
def memory_anomaly(duration):
    print(f"Starting Memory anomaly for {duration} seconds...")
    start_time = time.time()
    # Allocate around 500MB
    dummy_data = bytearray(500 * 1024 * 1024)
    while time.time() - start_time < duration:
        time.sleep(1)
    del dummy_data

def thread_anomaly(duration):
    print(f"Starting Thread anomaly for {duration} seconds...")
    start_time = time.time()
    
    def dummy_worker():
        while time.time() - start_time < duration:
            time.sleep(0.5)
            
    threads = []
    # Create 150 threads
    for _ in range(150):
        t = threading.Thread(target=dummy_worker)
        t.daemon = True
        t.start()
        threads.append(t)
        
    for t in threads:
        t.join(timeout=duration)

def io_anomaly(duration):
    print(f"Starting I/O anomaly for {duration} seconds...")
    start_time = time.time()
    while time.time() - start_time < duration:
        with open("dummy_io_file.tmp", "wb") as f:
            f.write(bytearray(10 * 1024 * 1024)) # write 10MB
        time.sleep(0.1)

def combined_anomaly(duration):
    print(f"Starting Combined anomaly for {duration} seconds...")
    # Do everything but maybe less intense so we don't crash the system
    t_cpu = threading.Thread(target=cpu_anomaly, args=(duration,))
    t_mem = threading.Thread(target=memory_anomaly, args=(duration,))
    t_thread = threading.Thread(target=thread_anomaly, args=(duration,))
    
    t_cpu.start()
    t_mem.start()
    t_thread.start()
    
    t_cpu.join()
    t_mem.join()
    t_thread.join()

if __name__ == "__main__":
    import ctypes
    # Rename process title for easier identification by ProcessGuard
    try:
        # this might only work on windows for changing console title, 
        # actual process name in psutil might remain python.exe, 
        # so we will rely on command line args or title if possible.
        ctypes.windll.kernel32.SetConsoleTitleW("ProcessGuard-DemoWorker")
    except:
        pass
        
    parser = argparse.ArgumentParser(description="ProcessGuard Demo Worker")
    parser.add_argument('--type', choices=['cpu', 'memory', 'thread', 'io', 'combined'], required=True)
    parser.add_argument('--duration', type=int, default=30)
    
    args = parser.parse_args()
    
    try:
        if args.type == 'cpu':
            cpu_anomaly(args.duration)
        elif args.type == 'memory':
            memory_anomaly(args.duration)
        elif args.type == 'thread':
            thread_anomaly(args.duration)
        elif args.type == 'io':
            io_anomaly(args.duration)
        elif args.type == 'combined':
            combined_anomaly(args.duration)
    except KeyboardInterrupt:
        print("Demo stopped manually.")
    
    print("Demo worker finished.")
