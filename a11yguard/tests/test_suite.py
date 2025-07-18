"""
Test suite orchestrator for accessibility testing.

This module provides a framework for running comprehensive
accessibility test suites with different test cases.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestCase:
    """Represents a single test case."""
    name: str
    description: str
    test_function: Callable
    category: str
    priority: str  # 'critical', 'high', 'medium', 'low'
    enabled: bool = True


@dataclass
class TestResult:
    """Represents the result of a test case."""
    test_name: str
    status: str  # 'passed', 'failed', 'error', 'skipped'
    message: str
    details: Optional[Dict[str, Any]] = None
    duration: float = 0.0
    timestamp: Optional[str] = None


class TestSuite:
    """Orchestrates and runs accessibility test suites."""
    
    def __init__(self, name: str = "Accessibility Test Suite"):
        """Initialize the TestSuite.
        
        Args:
            name: Name of the test suite
        """
        self.name = name
        self.test_cases: List[TestCase] = []
        self.results: List[TestResult] = []
        self.logger = logging.getLogger(__name__)
        
    def add_test_case(self, test_case: TestCase):
        """Add a test case to the suite.
        
        Args:
            test_case: TestCase to add
        """
        self.test_cases.append(test_case)
        self.logger.debug(f"Added test case: {test_case.name}")
    
    def add_test_cases(self, test_cases: List[TestCase]):
        """Add multiple test cases to the suite.
        
        Args:
            test_cases: List of TestCase objects to add
        """
        for test_case in test_cases:
            self.add_test_case(test_case)
    
    def run_suite(self, context: Optional[Dict[str, Any]] = None) -> List[TestResult]:
        """Run all test cases in the suite.
        
        Args:
            context: Optional context data to pass to test cases
            
        Returns:
            List of test results
        """
        if not context:
            context = {}
        
        self.results = []
        enabled_tests = [tc for tc in self.test_cases if tc.enabled]
        
        self.logger.info(f"Running test suite '{self.name}' with {len(enabled_tests)} test cases")
        
        for test_case in enabled_tests:
            result = self._run_test_case(test_case, context)
            self.results.append(result)
            
            # Log result
            status_emoji = {
                'passed': '✅',
                'failed': '❌',
                'error': '⚠️',
                'skipped': '⏭️'
            }
            
            self.logger.info(f"{status_emoji.get(result.status, '❓')} {test_case.name}: {result.message}")
        
        return self.results
    
    def _run_test_case(self, test_case: TestCase, context: Dict[str, Any]) -> TestResult:
        """Run a single test case.
        
        Args:
            test_case: TestCase to run
            context: Context data
            
        Returns:
            TestResult for the test case
        """
        start_time = time.time()
        
        try:
            self.logger.debug(f"Running test case: {test_case.name}")
            
            # Run the test function
            result = test_case.test_function(context)
            
            duration = time.time() - start_time
            
            if isinstance(result, dict):
                status = result.get('status', 'passed')
                message = result.get('message', 'Test completed')
                details = result.get('details')
            else:
                status = 'passed' if result else 'failed'
                message = 'Test passed' if result else 'Test failed'
                details = None
            
            return TestResult(
                test_name=test_case.name,
                status=status,
                message=message,
                details=details,
                duration=duration,
                timestamp=self._get_timestamp()
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Error running test case {test_case.name}: {str(e)}")
            
            return TestResult(
                test_name=test_case.name,
                status='error',
                message=f"Test error: {str(e)}",
                details={'error': str(e)},
                duration=duration,
                timestamp=self._get_timestamp()
            )
    
    def get_results_summary(self) -> Dict[str, Any]:
        """Get a summary of test results.
        
        Returns:
            Dictionary containing test summary
        """
        if not self.results:
            return {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'errors': 0,
                'skipped': 0,
                'success_rate': 0.0
            }
        
        status_counts = {}
        for result in self.results:
            status_counts[result.status] = status_counts.get(result.status, 0) + 1
        
        total_tests = len(self.results)
        passed = status_counts.get('passed', 0)
        success_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
        
        return {
            'total_tests': total_tests,
            'passed': passed,
            'failed': status_counts.get('failed', 0),
            'errors': status_counts.get('error', 0),
            'skipped': status_counts.get('skipped', 0),
            'success_rate': round(success_rate, 2)
        }
    
    def get_results_by_category(self) -> Dict[str, List[TestResult]]:
        """Get test results grouped by category.
        
        Returns:
            Dictionary mapping categories to test results
        """
        categorized_results = {}
        
        for result in self.results:
            # Find the corresponding test case
            test_case = next((tc for tc in self.test_cases if tc.name == result.test_name), None)
            category = test_case.category if test_case else 'unknown'
            
            if category not in categorized_results:
                categorized_results[category] = []
            
            categorized_results[category].append(result)
        
        return categorized_results
    
    def get_results_by_priority(self) -> Dict[str, List[TestResult]]:
        """Get test results grouped by priority.
        
        Returns:
            Dictionary mapping priorities to test results
        """
        prioritized_results = {}
        
        for result in self.results:
            # Find the corresponding test case
            test_case = next((tc for tc in self.test_cases if tc.name == result.test_name), None)
            priority = test_case.priority if test_case else 'unknown'
            
            if priority not in prioritized_results:
                prioritized_results[priority] = []
            
            prioritized_results[priority].append(result)
        
        return prioritized_results
    
    def filter_results(self, status: Optional[str] = None, 
                      category: Optional[str] = None,
                      priority: Optional[str] = None) -> List[TestResult]:
        """Filter test results by various criteria.
        
        Args:
            status: Filter by status
            category: Filter by category
            priority: Filter by priority
            
        Returns:
            Filtered list of test results
        """
        filtered_results = self.results
        
        if status:
            filtered_results = [r for r in filtered_results if r.status == status]
        
        if category:
            filtered_results = [r for r in filtered_results 
                              if any(tc.name == r.test_name and tc.category == category 
                                    for tc in self.test_cases)]
        
        if priority:
            filtered_results = [r for r in filtered_results 
                              if any(tc.name == r.test_name and tc.priority == priority 
                                    for tc in self.test_cases)]
        
        return filtered_results
    
    def export_results(self, format: str = 'json', file_path: Optional[str] = None) -> str:
        """Export test results to a file.
        
        Args:
            format: Export format ('json', 'csv', 'html')
            file_path: Optional file path
            
        Returns:
            Path to the exported file
        """
        if not file_path:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            file_path = f"test_results_{timestamp}.{format}"
        
        if format == 'json':
            return self._export_json(file_path)
        elif format == 'csv':
            return self._export_csv(file_path)
        elif format == 'html':
            return self._export_html(file_path)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json(self, file_path: str) -> str:
        """Export results as JSON."""
        import json
        
        export_data = {
            'suite_name': self.name,
            'summary': self.get_results_summary(),
            'results': [
                {
                    'test_name': r.test_name,
                    'status': r.status,
                    'message': r.message,
                    'details': r.details,
                    'duration': r.duration,
                    'timestamp': r.timestamp
                }
                for r in self.results
            ]
        }
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return file_path
    
    def _export_csv(self, file_path: str) -> str:
        """Export results as CSV."""
        import csv
        
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Test Name', 'Status', 'Message', 'Duration', 'Timestamp'])
            
            for result in self.results:
                writer.writerow([
                    result.test_name,
                    result.status,
                    result.message,
                    result.duration,
                    result.timestamp
                ])
        
        return file_path
    
    def _export_html(self, file_path: str) -> str:
        """Export results as HTML."""
        summary = self.get_results_summary()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Results - {self.name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .error {{ color: orange; }}
        .skipped {{ color: gray; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Test Results: {self.name}</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Total Tests:</strong> {summary['total_tests']}</p>
        <p><strong>Passed:</strong> <span class="passed">{summary['passed']}</span></p>
        <p><strong>Failed:</strong> <span class="failed">{summary['failed']}</span></p>
        <p><strong>Errors:</strong> <span class="error">{summary['errors']}</span></p>
        <p><strong>Skipped:</strong> <span class="skipped">{summary['skipped']}</span></p>
        <p><strong>Success Rate:</strong> {summary['success_rate']}%</p>
    </div>
    
    <h2>Detailed Results</h2>
    <table>
        <tr>
            <th>Test Name</th>
            <th>Status</th>
            <th>Message</th>
            <th>Duration</th>
            <th>Timestamp</th>
        </tr>
"""
        
        for result in self.results:
            html_content += f"""
        <tr>
            <td>{result.test_name}</td>
            <td class="{result.status}">{result.status}</td>
            <td>{result.message}</td>
            <td>{result.duration:.2f}s</td>
            <td>{result.timestamp}</td>
        </tr>
"""
        
        html_content += """
    </table>
</body>
</html>
"""
        
        with open(file_path, 'w') as f:
            f.write(html_content)
        
        return file_path
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat() 