import os
import sys
import subprocess
from filecmp import cmp

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

def compare_files(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        lines1 = [line.strip() for line in f1.readlines()]
        lines2 = [line.strip() for line in f2.readlines()]
    return lines1 == lines2

def run_test(test_dir):
    input_file = os.path.join(test_dir, "input.txt")
    expected_output_file = os.path.join(test_dir, "expected_output.txt")
    actual_output_file = os.path.join(test_dir, "actual_output.txt")
    
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(project_root, "src", "main.py"), 
             input_file, actual_output_file],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Test failed in {test_dir}. Error:\n{result.stderr}")
            return False

        if compare_files(expected_output_file, actual_output_file):
            print(f"Test passed in {test_dir}.")
            return True
        else:
            print(f"Test failed in {test_dir}. Output mismatch.")
            return False

    except Exception as e:
        print(f"Error running test in {test_dir}: {e}")
        return False

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    all_tests_passed = True

    for test_dir in ["test1", "test2", "test3"]:
        test_path = os.path.join(current_dir, test_dir)
        if os.path.isdir(test_path):
            print(f"\nRunning test in {test_path}")
            if not run_test(test_path):
                all_tests_passed = False

    if all_tests_passed:
        print("\nAll tests passed!")
        exit(0)
    else:
        print("\nSome tests failed.")
        exit(1)
