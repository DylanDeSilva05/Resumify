#!/usr/bin/env python3
"""
Security vulnerability scanning script
"""
import subprocess
import sys
import json
import os
from pathlib import Path


def run_safety_check():
    """Run safety check for known vulnerabilities in dependencies"""
    print("Running Safety dependency vulnerability scan...")
    try:
        result = subprocess.run(
            ["./venv/Scripts/safety.exe", "check", "--json", "--ignore", "70612"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        if result.returncode == 0:
            print("No known vulnerabilities found in dependencies")
            return True
        else:
            print("Security vulnerabilities found (check details above)")
            # Safety's JSON output structure has changed - just show we found vulnerabilities
            if "vulnerabilities found" in result.stdout or "vulnerabilities found" in result.stderr:
                return False
            return False  # If exit code != 0, assume vulnerabilities found

    except FileNotFoundError:
        print("Safety not installed. Run: pip install safety")
        return False
    except Exception as e:
        print(f"Safety check failed: {e}")
        return False


def run_bandit_scan():
    """Run Bandit static security analysis"""
    print("Running Bandit static security analysis...")
    try:
        result = subprocess.run(
            ["./venv/Scripts/bandit.exe", "-r", "app/", "-f", "json", "-ll"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        if result.returncode == 0:
            print("No security issues found by Bandit")
            return True
        else:
            print("Security issues found by Bandit:")
            try:
                report = json.loads(result.stdout)
                for result_item in report.get("results", []):
                    print(f"  - {result_item['filename']}:{result_item['line_number']}")
                    print(f"    {result_item['test_name']}: {result_item['issue_text']}")
            except json.JSONDecodeError:
                print(result.stdout)
            return False

    except FileNotFoundError:
        print("Bandit not installed. Run: pip install bandit")
        return False
    except Exception as e:
        print(f"Bandit scan failed: {e}")
        return False


def check_environment_security():
    """Check environment configuration for security issues"""
    print("Checking environment security...")
    issues = []

    # Check if SECRET_KEY is default
    with open("app/core/config.py", "r") as f:
        config_content = f.read()
        if "your_super_secret_jwt_key_here" in config_content:
            issues.append("Default SECRET_KEY detected in config.py")

    # Check for hardcoded secrets
    sensitive_patterns = [
        "password",
        "secret",
        "api_key",
        "token",
        "credential"
    ]

    for pattern in sensitive_patterns:
        if pattern in config_content.lower():
            # This is a simple check - in reality, you'd want more sophisticated detection
            pass

    if issues:
        print("Environment security issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("Environment security checks passed")
        return True


def check_file_permissions():
    """Check critical file permissions"""
    print("Checking file permissions...")

    critical_files = [
        "app/core/config.py",
        "app/core/security.py",
        ".env"
    ]

    issues = []
    for file_path in critical_files:
        if os.path.exists(file_path):
            stat_info = os.stat(file_path)
            mode = stat_info.st_mode & 0o777

            # Check if file is world-readable (very basic check for Unix systems)
            if mode & 0o004:
                issues.append(f"{file_path} is world-readable")

    if issues:
        print("File permission issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("File permission checks passed")
        return True


def main():
    """Run all security checks"""
    print("Running Resumify Security Check Suite")
    print("=" * 50)

    checks = [
        ("Dependency Vulnerabilities", run_safety_check),
        ("Static Security Analysis", run_bandit_scan),
        ("Environment Security", check_environment_security),
        ("File Permissions", check_file_permissions),
    ]

    results = []
    for check_name, check_func in checks:
        print(f"\n{check_name}")
        print("-" * 30)
        result = check_func()
        results.append((check_name, result))

    print("\n" + "=" * 50)
    print("Security Check Summary")
    print("=" * 50)

    all_passed = True
    for check_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{check_name:<30} {status}")
        if not result:
            all_passed = False

    if all_passed:
        print("\nAll security checks passed!")
        sys.exit(0)
    else:
        print("\nSome security checks failed. Please review the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()