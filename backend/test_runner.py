import glob
import subprocess
import sys

def run_tests():
    files = sorted(glob.glob("test_phase*.py"))
    print(f"Found {len(files)} test files.")
    for f in files:
        print(f"\n--- Running {f} ---")
        res = subprocess.run([sys.executable, f], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"PASS: {f}")
        else:
            print(f"FAIL: {f}")
            print("STDOUT:", res.stdout)
            print("STDERR:", res.stderr)

if __name__ == "__main__":
    run_tests()
