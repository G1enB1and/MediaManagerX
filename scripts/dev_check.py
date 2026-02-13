#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys


def run(cmd: list[str]) -> int:
    print("$", " ".join(cmd))
    return subprocess.run(cmd, check=False).returncode


def main() -> int:
    code = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"])
    if code != 0:
        print("\n❌ dev_check failed")
        return code

    print("\n✅ dev_check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
