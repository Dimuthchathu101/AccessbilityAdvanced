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
            
            # Check if there's an actual error (not None)
            if 'error' in result and result['error']:
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
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .summary {{
            background: #f8f9fa;
            padding: 30px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .summary h2 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.8em;
            font-weight: 600;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }}
        
        .metric-card.violations {{
            border-left: 4px solid #e74c3c;
        }}
        
        .metric-card.passes {{
            border-left: 4px solid #27ae60;
        }}
        
        .metric-card.errors {{
            border-left: 4px solid #f39c12;
        }}
        
        .metric-card.urls {{
            border-left: 4px solid #3498db;
        }}
        
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .metric-label {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .violations .metric-value {{
            color: #e74c3c;
        }}
        
        .passes .metric-value {{
            color: #27ae60;
        }}
        
        .errors .metric-value {{
            color: #f39c12;
        }}
        
        .urls .metric-value {{
            color: #3498db;
        }}
        
        .compliance-rate {{
            background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-top: 20px;
        }}
        
        .compliance-rate h3 {{
            font-size: 1.2em;
            margin-bottom: 10px;
        }}
        
        .compliance-percentage {{
            font-size: 3em;
            font-weight: bold;
        }}
        
        .results-section {{
            padding: 30px;
        }}
        
        .url-header {{
            background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
            color: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: 500;
        }}
        
        .violation {{
            background: #fff5f5;
            border: 1px solid #fed7d7;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        
        .violation h3 {{
            color: #c53030;
            margin-bottom: 10px;
            font-size: 1.2em;
        }}
        
        .violation-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .detail-item {{
            background: white;
            padding: 10px;
            border-radius: 5px;
            border-left: 3px solid #e74c3c;
        }}
        
        .detail-label {{
            font-weight: bold;
            color: #2d3748;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .detail-value {{
            color: #4a5568;
            margin-top: 5px;
        }}
        
        .pass {{
            background: #f0fff4;
            border: 1px solid #c6f6d5;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        
        .pass h3 {{
            color: #22543d;
            margin-bottom: 5px;
            font-size: 1.1em;
        }}
        
        .pass-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .pass .detail-item {{
            background: white;
            padding: 10px;
            border-radius: 5px;
            border-left: 3px solid #27ae60;
        }}
        
        .error {{
            background: #fffaf0;
            border: 1px solid #feb2b2;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
        }}
        
        .error strong {{
            color: #c05621;
        }}
        
        .hidden {{
            display: none;
        }}
        
        .violations-details {{
            background: #fff5f5;
            border: 1px solid #fed7d7;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            max-height: 70vh;
            overflow-y: auto;
            overflow-x: hidden;
        }}
        
        .violations-details h3 {{
            color: #c53030;
            margin-bottom: 15px;
            font-size: 1.3em;
            position: sticky;
            top: 0;
            background: #fff5f5;
            padding: 10px 0;
            z-index: 10;
        }}
        
        .passes-details {{
            background: #f0fff4;
            border: 1px solid #c6f6d5;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            max-height: 70vh;
            overflow-y: auto;
            overflow-x: hidden;
        }}
        
        .passes-details h3 {{
            color: #22543d;
            margin-bottom: 15px;
            font-size: 1.3em;
            position: sticky;
            top: 0;
            background: #f0fff4;
            padding: 10px 0;
            z-index: 10;
        }}
        
        .back-button {{
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 20px;
            font-size: 1em;
            position: sticky;
            top: 0;
            z-index: 20;
        }}
        
        .back-button:hover {{
            background: #2980b9;
        }}
        
        /* Custom scrollbar styling */
        .violations-details::-webkit-scrollbar,
        .passes-details::-webkit-scrollbar {{
            width: 8px;
        }}
        
        .violations-details::-webkit-scrollbar-track,
        .passes-details::-webkit-scrollbar-track {{
            background: #f1f1f1;
            border-radius: 4px;
        }}
        
        .violations-details::-webkit-scrollbar-thumb,
        .passes-details::-webkit-scrollbar-thumb {{
            background: #c1c1c1;
            border-radius: 4px;
        }}
        
        .violations-details::-webkit-scrollbar-thumb:hover,
        .passes-details::-webkit-scrollbar-thumb:hover {{
            background: #a8a8a8;
        }}
        
        /* Firefox scrollbar styling */
        .violations-details,
        .passes-details {{
            scrollbar-width: thin;
            scrollbar-color: #c1c1c1 #f1f1f1;
        }}
        
        @media (max-width: 768px) {{
            .metrics-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .violation-details {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Accessibility Test Report</h1>
            <p>Comprehensive accessibility analysis results</p>
        </div>
        
        <div class="summary">
            <h2>📊 Test Summary</h2>
            <div class="metrics-grid">
                <div class="metric-card urls">
                    <div class="metric-value">{summary['urls_tested']}</div>
                    <div class="metric-label">URLs Tested</div>
                </div>
                <div class="metric-card violations" onclick="showViolations()">
                    <div class="metric-value">{summary['total_violations']}</div>
                    <div class="metric-label">Total Violations</div>
                </div>
                <div class="metric-card passes" onclick="showPasses()">
                    <div class="metric-value">{summary['total_passes']}</div>
                    <div class="metric-label">Total Passes</div>
                </div>
                <div class="metric-card errors">
                    <div class="metric-value">{summary['total_errors']}</div>
                    <div class="metric-label">Test Errors</div>
                </div>
            </div>
            
            <div class="compliance-rate">
                <h3>🎯 Compliance Rate</h3>
                <div class="compliance-percentage">{summary['compliance_rate']}%</div>
            </div>
            
            <p style="margin-top: 20px; color: #7f8c8d; font-size: 0.9em;">
                <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </div>
        
        <div id="violations-details" class="violations-details hidden">
            <button class="back-button" onclick="hideViolations()">← Back to Summary</button>
            <h3>🚨 All Violations Found</h3>
            <div id="violations-list"></div>
        </div>
        
        <div id="passes-details" class="passes-details hidden">
            <button class="back-button" onclick="hidePasses()">← Back to Summary</button>
            <h3>✅ All Passed Checks</h3>
            <div id="passes-list"></div>
        </div>
        
        <div id="results-section" class="results-section">
"""
        
        # Collect all violations and passes for the details sections
        all_violations = []
        all_passes = []
        
        for result in results:
            url = result.get('url', 'Unknown URL')
            html += f'<div class="url-header">🌐 {url}</div>'
            
            if 'error' in result and result['error']:
                html += f'<div class="error"><strong>Error:</strong> {result["error"]}</div>'
                continue
            
            if 'results' in result and result['results']:
                violations = result['results'].get('violations', [])
                passes = result['results'].get('passes', [])
                
                # Add violations to the collection
                for violation in violations:
                    violation['url'] = url
                    all_violations.append(violation)
                
                # Add passes to the collection
                for pass_result in passes:
                    pass_result['url'] = url
                    all_passes.append(pass_result)
                
                for violation in violations:
                    html += f"""
                    <div class="violation">
                        <h3>❌ {violation.get('help', 'Unknown Rule')}</h3>
                        <div class="violation-details">
                            <div class="detail-item">
                                <div class="detail-label">Impact</div>
                                <div class="detail-value">{violation.get('impact', 'Unknown')}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Description</div>
                                <div class="detail-value">{violation.get('description', 'No description')}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Help URL</div>
                                <div class="detail-value">
                                    <a href="{violation.get('helpUrl', '#')}" target="_blank" style="color: #3498db;">
                                        View Documentation
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                    """
                
                for pass_result in passes:
                    html += f"""
                    <div class="pass">
                        <h3>✅ {pass_result.get('help', 'Unknown Rule')}</h3>
                        <div class="pass-details">
                            <div class="detail-item">
                                <div class="detail-label">Description</div>
                                <div class="detail-value">{pass_result.get('description', 'No description')}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Help URL</div>
                                <div class="detail-value">
                                    <a href="{pass_result.get('helpUrl', '#')}" target="_blank" style="color: #3498db;">
                                        View Documentation
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                    """
        
        # Generate JavaScript for violations list
        violations_js = ""
        for i, violation in enumerate(all_violations):
            violations_js += f"""
            <div class="violation">
                <h3>❌ {violation.get('help', 'Unknown Rule')}</h3>
                <p><strong>URL:</strong> {violation.get('url', 'Unknown')}</p>
                <div class="violation-details">
                    <div class="detail-item">
                        <div class="detail-label">Impact</div>
                        <div class="detail-value">{violation.get('impact', 'Unknown')}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Description</div>
                        <div class="detail-value">{violation.get('description', 'No description')}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Help URL</div>
                        <div class="detail-value">
                            <a href="{violation.get('helpUrl', '#')}" target="_blank" style="color: #3498db;">
                                View Documentation
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            """
        
        # Generate JavaScript for passes list
        passes_js = ""
        for i, pass_result in enumerate(all_passes):
            passes_js += f"""
            <div class="pass">
                <h3>✅ {pass_result.get('help', 'Unknown Rule')}</h3>
                <p><strong>URL:</strong> {pass_result.get('url', 'Unknown')}</p>
                <div class="pass-details">
                    <div class="detail-item">
                        <div class="detail-label">Description</div>
                        <div class="detail-value">{pass_result.get('description', 'No description')}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Help URL</div>
                        <div class="detail-value">
                            <a href="{pass_result.get('helpUrl', '#')}" target="_blank" style="color: #3498db;">
                                View Documentation
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            """
        
        html += f"""
        </div>
    </div>
    
    <script>
        function showViolations() {{
            document.getElementById('violations-details').classList.remove('hidden');
            document.getElementById('passes-details').classList.add('hidden');
            document.getElementById('results-section').classList.add('hidden');
            document.getElementById('violations-list').innerHTML = `{violations_js}`;
        }}
        
        function showPasses() {{
            document.getElementById('passes-details').classList.remove('hidden');
            document.getElementById('violations-details').classList.add('hidden');
            document.getElementById('results-section').classList.add('hidden');
            document.getElementById('passes-list').innerHTML = `{passes_js}`;
        }}
        
        function hideViolations() {{
            document.getElementById('violations-details').classList.add('hidden');
            document.getElementById('results-section').classList.remove('hidden');
        }}
        
        function hidePasses() {{
            document.getElementById('passes-details').classList.add('hidden');
            document.getElementById('results-section').classList.remove('hidden');
        }}
    </script>
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