"""
Report generation for accessibility test results.

This module handles the generation of various report formats
for accessibility testing results.
"""

import json
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import asdict


class ReportGenerator:
    """Generates accessibility test reports in various formats."""
    
    def __init__(self, output_dir: str = "outputs/reports"):
        """Initialize the ReportGenerator.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def generate_json_report(self, results: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """Generate a JSON report from test results.
        
        Args:
            results: List of test results
            filename: Optional custom filename
            
        Returns:
            Path to the generated report
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"accessibility_report_{timestamp}.json"
        
        report_path = self.output_dir / filename
        
        report_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_tests": len(results),
                "tool_version": "a11yguard-1.0.0"
            },
            "summary": self._generate_summary(results),
            "results": results
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"JSON report generated: {report_path}")
        return str(report_path)
    
    def generate_html_report(self, results: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """Generate an HTML report from test results.
        
        Args:
            results: List of test results
            filename: Optional custom filename
            
        Returns:
            Path to the generated report
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"accessibility_report_{timestamp}.html"
        
        report_path = self.output_dir / filename
        
        html_content = self._generate_html_content(results)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML report generated: {report_path}")
        return str(report_path)
    
    def generate_csv_report(self, results: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """Generate a CSV report from test results.
        
        Args:
            results: List of test results
            filename: Optional custom filename
            
        Returns:
            Path to the generated report
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"accessibility_report_{timestamp}.csv"
        
        report_path = self.output_dir / filename
        
        # Flatten results for CSV
        flattened_results = []
        for result in results:
            url = result.get('url', '')
            timestamp = result.get('timestamp', '')
            
            if 'results' in result and result['results']:
                violations = result['results'].get('violations', [])
                for violation in violations:
                    for node in violation.get('nodes', []):
                        flattened_results.append({
                            'url': url,
                            'timestamp': timestamp,
                            'rule_id': violation.get('id', ''),
                            'rule_name': violation.get('help', ''),
                            'severity': violation.get('impact', ''),
                            'element': node.get('html', ''),
                            'message': violation.get('description', '')
                        })
            elif 'error' in result:
                flattened_results.append({
                    'url': url,
                    'timestamp': timestamp,
                    'rule_id': 'ERROR',
                    'rule_name': 'Test Error',
                    'severity': 'error',
                    'element': '',
                    'message': result['error']
                })
        
        if flattened_results:
            fieldnames = flattened_results[0].keys()
            with open(report_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(flattened_results)
        
        self.logger.info(f"CSV report generated: {report_path}")
        return str(report_path)
    
    def generate_markdown_report(self, results: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """Generate a Markdown report from test results.
        
        Args:
            results: List of test results
            filename: Optional custom filename
            
        Returns:
            Path to the generated report
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"accessibility_report_{timestamp}.md"
        
        report_path = self.output_dir / filename
        
        markdown_content = self._generate_markdown_content(results)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        self.logger.info(f"Markdown report generated: {report_path}")
        return str(report_path)
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of test results."""
        total_violations = 0
        total_passes = 0
        total_errors = 0
        urls_tested = set()
        
        for result in results:
            urls_tested.add(result.get('url', ''))
            
            if 'error' in result:
                total_errors += 1
                continue
            
            if 'results' in result and result['results']:
                violations = result['results'].get('violations', [])
                passes = result['results'].get('passes', [])
                
                total_violations += len(violations)
                total_passes += len(passes)
        
        return {
            "urls_tested": len(urls_tested),
            "total_violations": total_violations,
            "total_passes": total_passes,
            "total_errors": total_errors,
            "compliance_rate": self._calculate_compliance_rate(total_violations, total_passes)
        }
    
    def _calculate_compliance_rate(self, violations: int, passes: int) -> float:
        """Calculate compliance rate as a percentage."""
        total = violations + passes
        if total == 0:
            return 0.0
        return round((passes / total) * 100, 2)
    
    def _generate_html_content(self, results: List[Dict[str, Any]]) -> str:
        """Generate HTML content for the report."""
        summary = self._generate_summary(results)
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accessibility Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .violation {{ background: #ffe6e6; border-left: 4px solid #ff4444; padding: 10px; margin: 10px 0; }}
        .pass {{ background: #e6ffe6; border-left: 4px solid #44ff44; padding: 10px; margin: 10px 0; }}
        .error {{ background: #ffe6cc; border-left: 4px solid #ff8800; padding: 10px; margin: 10px 0; }}
        .url-header {{ background: #333; color: white; padding: 10px; margin: 20px 0 10px 0; }}
    </style>
</head>
<body>
    <h1>Accessibility Test Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>URLs Tested:</strong> {summary['urls_tested']}</p>
        <p><strong>Total Violations:</strong> {summary['total_violations']}</p>
        <p><strong>Total Passes:</strong> {summary['total_passes']}</p>
        <p><strong>Compliance Rate:</strong> {summary['compliance_rate']}%</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
"""
        
        for result in results:
            url = result.get('url', 'Unknown URL')
            html += f'<div class="url-header">{url}</div>'
            
            if 'error' in result:
                html += f'<div class="error"><strong>Error:</strong> {result["error"]}</div>'
                continue
            
            if 'results' in result and result['results']:
                violations = result['results'].get('violations', [])
                passes = result['results'].get('passes', [])
                
                for violation in violations:
                    html += f"""
                    <div class="violation">
                        <h3>{violation.get('help', 'Unknown Rule')}</h3>
                        <p><strong>Impact:</strong> {violation.get('impact', 'Unknown')}</p>
                        <p><strong>Description:</strong> {violation.get('description', 'No description')}</p>
                        <p><strong>Help:</strong> {violation.get('helpUrl', 'No help URL')}</p>
                    </div>
                    """
                
                for pass_result in passes:
                    html += f"""
                    <div class="pass">
                        <h3>{pass_result.get('help', 'Unknown Rule')} ✓</h3>
                        <p><strong>Description:</strong> {pass_result.get('description', 'No description')}</p>
                    </div>
                    """
        
        html += """
</body>
</html>
"""
        return html
    
    def _generate_markdown_content(self, results: List[Dict[str, Any]]) -> str:
        """Generate Markdown content for the report."""
        summary = self._generate_summary(results)
        
        markdown = f"""# Accessibility Test Report

## Summary

- **URLs Tested:** {summary['urls_tested']}
- **Total Violations:** {summary['total_violations']}
- **Total Passes:** {summary['total_passes']}
- **Compliance Rate:** {summary['compliance_rate']}%
- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Detailed Results

"""
        
        for result in results:
            url = result.get('url', 'Unknown URL')
            markdown += f"### {url}\n\n"
            
            if 'error' in result:
                markdown += f"**Error:** {result['error']}\n\n"
                continue
            
            if 'results' in result and result['results']:
                violations = result['results'].get('violations', [])
                passes = result['results'].get('passes', [])
                
                if violations:
                    markdown += "#### Violations\n\n"
                    for violation in violations:
                        markdown += f"- **{violation.get('help', 'Unknown Rule')}** ({violation.get('impact', 'Unknown')})\n"
                        markdown += f"  - {violation.get('description', 'No description')}\n"
                        markdown += f"  - Help: {violation.get('helpUrl', 'No help URL')}\n\n"
                
                if passes:
                    markdown += "#### Passes\n\n"
                    for pass_result in passes:
                        markdown += f"- **{pass_result.get('help', 'Unknown Rule')}** ✓\n"
                        markdown += f"  - {pass_result.get('description', 'No description')}\n\n"
        
        return markdown 