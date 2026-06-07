#!/usr/bin/env python3
import sys

name = sys.argv[1] if len(sys.argv) > 1 else "World"
verbose = "--verbose" in sys.argv or "-v" in sys.argv

if verbose:
    print(f"[DEBUG] 正在执行 Hello 脚本...")

print(f"Hello, {name}!")

if verbose:
    print(f"[DEBUG] 脚本执行完成")
