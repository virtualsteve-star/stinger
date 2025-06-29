#!/usr/bin/env python3
"""
Automated Test Runner for Stinger Web Demo

This script runs the complete test suite including:
1. Backend unit tests
2. Frontend unit tests  
3. End-to-end system tests
4. Integration tests with browser automation

The script is designed to run completely automated without user intervention,
providing comprehensive validation of the entire demo system.

Usage:
    python run_all_tests.py [options]
    
Options:
    --quick        Run only fast unit tests (skip E2E)
    --e2e-only     Run only end-to-end tests
    --no-cleanup   Don't clean up processes after tests
    --verbose      Show verbose output
    --parallel     Run tests in parallel where possible
    
Exit codes:
    0: All tests passed
    1: Some tests failed
    2: Test environment setup failed
"""

import sys
import os
import argparse
import subprocess
import time
import json
import signal
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile

class AutomatedTestRunner:
    def __init__(self, args):
        self.demo_dir = Path(__file__).parent
        self.backend_dir = self.demo_dir / "backend"
        self.frontend_dir = self.demo_dir / "frontend"
        self.args = args
        self.test_results = {}
        self.processes = []
        
    def log(self, message, level="INFO"):
        """Log a message with timestamp."""
        if level == "DEBUG" and not self.args.verbose:
            return
            
        timestamp = time.strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "DEBUG": "🔍"
        }.get(level, "ℹ️")
        print(f"[{timestamp}] {prefix} {message}")
        
    def run_command(self, cmd, cwd=None, timeout=300, capture_output=True):
        """Run a command and return success status and output."""
        try:
            self.log(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}", "DEBUG")
            
            if isinstance(cmd, str):
                cmd = cmd.split()
                
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            self.log(f"Command timed out: {cmd}", "ERROR")
            return False, "", "Command timed out"
        except Exception as e:
            self.log(f"Command failed: {e}", "ERROR")
            return False, "", str(e)
    
    def check_dependencies(self):
        """Check that all required dependencies are available."""
        self.log("Checking test dependencies...")
        
        # Check Python dependencies
        python_deps = ['pytest', 'fastapi', 'uvicorn', 'requests']
        for dep in python_deps:
            success, _, _ = self.run_command([sys.executable, "-c", f"import {dep}"])
            if not success:
                self.log(f"Missing Python dependency: {dep}", "ERROR")
                return False
        
        # Check Node.js and npm
        success, _, _ = self.run_command(["node", "--version"])
        if not success:
            self.log("Node.js not found", "ERROR")
            return False
            
        success, _, _ = self.run_command(["npm", "--version"])
        if not success:
            self.log("npm not found", "ERROR")
            return False
        
        # Check frontend dependencies
        if not (self.frontend_dir / "node_modules").exists():
            self.log("Installing frontend dependencies...", "WARNING")
            success, stdout, stderr = self.run_command(["npm", "install"], cwd=self.frontend_dir, timeout=180)
            if not success:
                self.log(f"Failed to install frontend deps: {stderr}", "ERROR")
                return False
        
        # Check for optional dependencies
        try:
            import playwright
            self.log("Playwright available for integration tests", "DEBUG")
        except ImportError:
            self.log("Playwright not available - integration tests will be skipped", "WARNING")
        
        self.log("All dependencies checked", "SUCCESS")
        return True
    
    def run_backend_tests(self):
        """Run backend unit and API tests."""
        self.log("Running backend tests...")
        
        # Run comprehensive backend tests
        success, stdout, stderr = self.run_command([
            sys.executable, "-m", "pytest", 
            "test_main.py", 
            "-v", 
            "--tb=short",
            f"--maxfail={5 if self.args.quick else 0}"
        ], cwd=self.backend_dir, timeout=300)
        
        self.test_results['backend_unit'] = {
            'success': success,
            'stdout': stdout,
            'stderr': stderr
        }
        
        if success:
            self.log("Backend tests PASSED", "SUCCESS")
        else:
            self.log("Backend tests FAILED", "ERROR")
            if self.args.verbose:
                self.log(f"STDOUT: {stdout}")
                self.log(f"STDERR: {stderr}")
        
        return success
    
    def run_frontend_tests(self):
        """Run frontend unit tests."""
        self.log("Running frontend tests...")
        
        # Set environment variables for testing
        env = os.environ.copy()
        env['CI'] = 'true'  # Prevents interactive mode
        env['SKIP_PREFLIGHT_CHECK'] = 'true'
        
        # Run React tests
        success, stdout, stderr = self.run_command([
            "npm", "test", "--", 
            "--coverage", 
            "--verbose",
            "--watchAll=false",
            "--testPathIgnorePatterns=/node_modules/",
            f"--maxWorkers={2 if self.args.quick else 4}"
        ], cwd=self.frontend_dir, timeout=300)
        
        self.test_results['frontend_unit'] = {
            'success': success,
            'stdout': stdout,
            'stderr': stderr
        }
        
        if success:
            self.log("Frontend tests PASSED", "SUCCESS")
        else:
            self.log("Frontend tests FAILED", "ERROR")
            if self.args.verbose:
                self.log(f"STDOUT: {stdout}")
                self.log(f"STDERR: {stderr}")
        
        return success
    
    def run_e2e_system_tests(self):
        """Run end-to-end system tests."""
        if self.args.quick:
            self.log("Skipping E2E tests in quick mode")
            return True
            
        self.log("Running E2E system tests...")
        
        # Run the existing e2e test suite
        success, stdout, stderr = self.run_command([
            sys.executable, "test_demo_e2e.py", "--cleanup"
        ], cwd=self.demo_dir, timeout=600)
        
        self.test_results['e2e_system'] = {
            'success': success,
            'stdout': stdout,
            'stderr': stderr
        }
        
        if success:
            self.log("E2E system tests PASSED", "SUCCESS")
        else:
            self.log("E2E system tests FAILED", "ERROR")
            if self.args.verbose:
                self.log(f"STDOUT: {stdout}")
                self.log(f"STDERR: {stderr}")
        
        return success
    
    def run_integration_tests(self):
        """Run integration tests with browser automation."""
        if self.args.quick:
            self.log("Skipping integration tests in quick mode")
            return True
        
        # Check if Playwright is available
        try:
            import playwright
        except ImportError:
            self.log("Playwright not available - skipping integration tests", "WARNING")
            return True
        
        self.log("Running integration tests with browser automation...")
        
        success, stdout, stderr = self.run_command([
            sys.executable, "test_integration_e2e.py"
        ], cwd=self.demo_dir, timeout=900)
        
        self.test_results['integration'] = {
            'success': success,
            'stdout': stdout,
            'stderr': stderr
        }
        
        if success:
            self.log("Integration tests PASSED", "SUCCESS")
        else:
            self.log("Integration tests FAILED", "ERROR")
            if self.args.verbose:
                self.log(f"STDOUT: {stdout}")
                self.log(f"STDERR: {stderr}")
        
        return success
    
    def run_parallel_tests(self):
        """Run tests in parallel where possible."""
        self.log("Running tests in parallel...")
        
        # Tests that can run in parallel (unit tests)
        parallel_tests = []
        if not self.args.e2e_only:
            parallel_tests = [
                ("Backend Unit Tests", self.run_backend_tests),
                ("Frontend Unit Tests", self.run_frontend_tests)
            ]
        
        # Tests that must run sequentially (E2E tests that use ports)
        sequential_tests = []
        if not self.args.quick or self.args.e2e_only:
            sequential_tests = [
                ("E2E System Tests", self.run_e2e_system_tests),
                ("Integration Tests", self.run_integration_tests)
            ]
        
        all_passed = True
        
        # Run parallel tests
        if parallel_tests:
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_to_test = {
                    executor.submit(test_func): test_name 
                    for test_name, test_func in parallel_tests
                }
                
                for future in as_completed(future_to_test):
                    test_name = future_to_test[future]
                    try:
                        success = future.result()
                        if not success:
                            all_passed = False
                            self.log(f"{test_name} failed", "ERROR")
                    except Exception as e:
                        all_passed = False
                        self.log(f"{test_name} raised exception: {e}", "ERROR")
        
        # Run sequential tests
        for test_name, test_func in sequential_tests:
            try:
                success = test_func()
                if not success:
                    all_passed = False
            except Exception as e:
                all_passed = False
                self.log(f"{test_name} raised exception: {e}", "ERROR")
        
        return all_passed
    
    def run_sequential_tests(self):
        """Run all tests sequentially."""
        self.log("Running tests sequentially...")
        
        all_passed = True
        
        if not self.args.e2e_only:
            if not self.run_backend_tests():
                all_passed = False
            if not self.run_frontend_tests():
                all_passed = False
        
        if not self.args.quick or self.args.e2e_only:
            if not self.run_e2e_system_tests():
                all_passed = False
            if not self.run_integration_tests():
                all_passed = False
        
        return all_passed
    
    def generate_test_report(self):
        """Generate a comprehensive test report."""
        self.log("Generating test report...")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        
        print("\n" + "=" * 80)
        print("📊 STINGER WEB DEMO TEST REPORT")
        print("=" * 80)
        print(f"Total Test Suites: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "No tests run")
        print()
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")
            
            if not result['success'] and self.args.verbose:
                print(f"  Error output: {result['stderr'][:200]}...")
        
        print("=" * 80)
        
        # Save detailed report to file
        report_file = self.demo_dir / "test_report.json"
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_suites': total_tests,
                'passed_suites': passed_tests,
                'success_rate': passed_tests/total_tests*100 if total_tests > 0 else 0,
                'results': self.test_results
            }, f, indent=2)
        
        self.log(f"Detailed report saved to: {report_file}")
        
        return passed_tests == total_tests
    
    def cleanup(self):
        """Clean up any running processes."""
        if self.args.no_cleanup:
            self.log("Skipping cleanup due to --no-cleanup flag")
            return
        
        self.log("Cleaning up test environment...")
        
        # Kill any processes we started
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        
        # Kill any processes on demo ports
        for port in [3000, 8000]:
            try:
                subprocess.run(f"lsof -ti:{port} | xargs kill -9", 
                             shell=True, capture_output=True)
            except:
                pass
    
    def run_all_tests(self):
        """Run the complete automated test suite."""
        self.log("🚀 Starting Stinger Web Demo Automated Test Suite")
        self.log("=" * 80)
        
        start_time = time.time()
        
        # Check dependencies first
        if not self.check_dependencies():
            self.log("Dependency check failed - aborting tests", "ERROR")
            return False
        
        try:
            # Run tests (parallel or sequential based on args)
            if self.args.parallel and not self.args.e2e_only:
                success = self.run_parallel_tests()
            else:
                success = self.run_sequential_tests()
            
            # Generate report
            report_success = self.generate_test_report()
            
            end_time = time.time()
            duration = end_time - start_time
            
            if success and report_success:
                self.log(f"🎉 ALL TESTS PASSED! (Duration: {duration:.1f}s)", "SUCCESS")
                return True
            else:
                self.log(f"❌ TESTS FAILED (Duration: {duration:.1f}s)", "ERROR")
                return False
                
        except KeyboardInterrupt:
            self.log("Tests interrupted by user", "WARNING")
            return False
        except Exception as e:
            self.log(f"Test suite failed with exception: {e}", "ERROR")
            return False
        finally:
            self.cleanup()

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automated test runner for Stinger Web Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_all_tests.py                 # Run all tests
  python run_all_tests.py --quick         # Run only fast unit tests
  python run_all_tests.py --e2e-only      # Run only E2E tests
  python run_all_tests.py --parallel      # Run tests in parallel
        """
    )
    
    parser.add_argument('--quick', action='store_true',
                       help='Run only fast unit tests (skip E2E)')
    parser.add_argument('--e2e-only', action='store_true',
                       help='Run only end-to-end tests')
    parser.add_argument('--no-cleanup', action='store_true',
                       help="Don't clean up processes after tests")
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show verbose output')
    parser.add_argument('--parallel', action='store_true',
                       help='Run tests in parallel where possible')
    
    args = parser.parse_args()
    
    # Validate argument combinations
    if args.quick and args.e2e_only:
        print("❌ ERROR: --quick and --e2e-only are mutually exclusive")
        sys.exit(2)
    
    runner = AutomatedTestRunner(args)
    
    # Set up signal handlers for clean shutdown
    def signal_handler(sig, frame):
        runner.log("Received interrupt signal, cleaning up...", "WARNING")
        runner.cleanup()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the test suite
    success = runner.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()