import subprocess


def run_k6_test():
    result = subprocess.run(
        ["k6", "run", "k6/test.js"],
        capture_output=True,
        text=True
    )

    return {
        "success": result.returncode == 0,
        "output": result.stdout,
        "error": result.stderr,
    }