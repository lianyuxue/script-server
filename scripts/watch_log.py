#!/usr/bin/env python3
"""
Script to watch and display server log in real-time
Compatible with Script Server
"""
import time
import sys
import os

def follow(filename):
    """Follow a file like tail -f"""
    with open(filename, 'r') as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line

def main():
    # Default values
    num_lines = 50
    log_file = '/Users/lianyuxue/Documents/TraeSOLO/script-server/logs/server.log'
    
    # First try environment variables (more reliable)
    if 'PARAM_LINES' in os.environ:
        try:
            num_lines = int(os.environ['PARAM_LINES'])
        except ValueError:
            pass
    if 'PARAM_FILE' in os.environ:
        log_file = os.environ['PARAM_FILE']
    
    # Fallback to positional arguments
    args = sys.argv[1:]
    if len(args) >= 1 and 'PARAM_LINES' not in os.environ:
        try:
            num_lines = int(args[0])
        except ValueError:
            pass
    if len(args) >= 2 and 'PARAM_FILE' not in os.environ:
        log_file = args[1]
    
    if not os.path.exists(log_file):
        print(f"Error: Log file not found: {log_file}")
        return 1
    
    # Show last N lines first
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            print(f"\n=== Last {num_lines} lines of log ===\n")
            for line in lines[-num_lines:]:
                print(line, end='')
            print(f"\n=== Watching {log_file}... (Press Ctrl+C to stop) ===\n")
            
            # Now follow the file
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                print(line, end='')
                
    except KeyboardInterrupt:
        print("\n\nStopped watching log.")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
