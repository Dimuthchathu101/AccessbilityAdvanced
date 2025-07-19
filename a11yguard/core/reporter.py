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
        
        .url-summary {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .url-summary .url-info {{
            flex: 1;
        }}
        
        .url-summary .url-stats {{
            display: flex;
            gap: 15px;
        }}
        
        .url-stat {{
            text-align: center;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        
        .url-stat.violations {{
            background: #fed7d7;
            color: #c53030;
        }}
        
        .url-stat.passes {{
            background: #c6f6d5;
            color: #22543d;
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
        
        .urls-details {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            max-height: 70vh;
            overflow-y: auto;
            overflow-x: hidden;
        }}
        
        .urls-details h3 {{
            color: #3498db;
            margin-bottom: 15px;
            font-size: 1.3em;
            position: sticky;
            top: 0;
            background: #f8f9fa;
            padding: 10px 0;
            z-index: 10;
        }}
        
        .errors-details {{
            background: #fffaf0;
            border: 1px solid #feb2b2;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            max-height: 70vh;
            overflow-y: auto;
            overflow-x: hidden;
        }}
        
        .errors-details h3 {{
            color: #f39c12;
            margin-bottom: 15px;
            font-size: 1.3em;
            position: sticky;
            top: 0;
            background: #fffaf0;
            padding: 10px 0;
            z-index: 10;
        }}
        
        .url-item {{
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        
        .url-item h4 {{
            color: #3498db;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        
        .url-item-stats {{
            display: flex;
            gap: 15px;
            margin-top: 10px;
        }}
        
        .url-item-stat {{
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        
        .url-item-stat.violations {{
            background: #fed7d7;
            color: #c53030;
        }}
        
        .url-item-stat.passes {{
            background: #c6f6d5;
            color: #22543d;
        }}
        
        .error-item {{
            background: white;
            border: 1px solid #feb2b2;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        
        .error-item h4 {{
            color: #f39c12;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        
        .error-item .error-message {{
            color: #c05621;
            font-weight: bold;
            margin-top: 10px;
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
        
        .url-section {{
            margin: 20px 0;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            overflow: hidden;
        }}
        
        .url-section-header {{
            background: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 1px solid #e9ecef;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .url-section-content {{
            padding: 20px;
        }}
        
        /* Custom scrollbar styling */
        .violations-details::-webkit-scrollbar,
        .passes-details::-webkit-scrollbar,
        .urls-details::-webkit-scrollbar,
        .errors-details::-webkit-scrollbar {{
            width: 8px;
        }}
        
        .violations-details::-webkit-scrollbar-track,
        .passes-details::-webkit-scrollbar-track,
        .urls-details::-webkit-scrollbar-track,
        .errors-details::-webkit-scrollbar-track {{
            background: #f1f1f1;
            border-radius: 4px;
        }}
        
        .violations-details::-webkit-scrollbar-thumb,
        .passes-details::-webkit-scrollbar-thumb,
        .urls-details::-webkit-scrollbar-thumb,
        .errors-details::-webkit-scrollbar-thumb {{
            background: #c1c1c1;
            border-radius: 4px;
        }}
        
        .violations-details::-webkit-scrollbar-thumb:hover,
        .passes-details::-webkit-scrollbar-thumb:hover,
        .urls-details::-webkit-scrollbar-thumb:hover,
        .errors-details::-webkit-scrollbar-thumb:hover {{
            background: #a8a8a8;
        }}
        
        /* Firefox scrollbar styling */
        .violations-details,
        .passes-details,
        .urls-details,
        .errors-details {{
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
            
            .url-summary .url-stats {{
                flex-direction: column;
                gap: 5px;
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
                <div class="metric-card urls" onclick="showUrls()">
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
                <div class="metric-card errors" onclick="showErrors()">
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
        
        <div id="urls-details" class="urls-details hidden">
            <button class="back-button" onclick="hideUrls()">← Back to Summary</button>
            <h3>🌐 All URLs Tested</h3>
            <div id="urls-list"></div>
        </div>
        
        <div id="errors-details" class="errors-details hidden">
            <button class="back-button" onclick="hideErrors()">← Back to Summary</button>
            <h3>⚠️ All Test Errors</h3>
            <div id="errors-list"></div>
        </div>
        
        <div id="results-section" class="results-section">
            <h2 style="color: #2c3e50; margin-bottom: 20px;">🌐 URLs Tested</h2>
"""
        
        # Collect all violations and passes for the details sections
        all_violations = []
        all_passes = []
        
        for result in results:
            url = result.get('url', 'Unknown URL')
            violations = []
            passes = []
            
            if 'error' in result and result['error']:
                # Handle error case
                html += f"""
                <div class="url-section">
                    <div class="url-section-header">🌐 {url}</div>
                    <div class="url-section-content">
                        <div class="error"><strong>Error:</strong> {result["error"]}</div>
                    </div>
                </div>
                """
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
            
            # Create URL section with summary
            html += f"""
            <div class="url-section">
                <div class="url-section-header">🌐 {url}</div>
                <div class="url-section-content">
                    <div class="url-summary">
                        <div class="url-info">
                            <strong>URL:</strong> {url}
                        </div>
                        <div class="url-stats">
                            <div class="url-stat violations">{len(violations)} Violations</div>
                            <div class="url-stat passes">{len(passes)} Passes</div>
                        </div>
                    </div>
            """
            
            # Add violations for this URL
            if violations:
                html += '<h3 style="color: #c53030; margin: 20px 0 10px 0;">❌ Violations</h3>'
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
            
            # Add passes for this URL
            if passes:
                html += '<h3 style="color: #22543d; margin: 20px 0 10px 0;">✅ Passes</h3>'
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
            
            html += """
                </div>
            </div>
            """
        
        # Generate JavaScript for violations list with URL grouping
        violations_js = ""
        current_url = None
        for violation in all_violations:
            if violation.get('url') != current_url:
                if current_url is not None:
                    violations_js += "</div>"
                current_url = violation.get('url')
                violations_js += f'<h4 style="color: #c53030; margin: 20px 0 10px 0; padding: 10px; background: #fed7d7; border-radius: 5px;">🌐 {current_url}</h4><div style="margin-left: 20px;">'
            
            violations_js += f"""
            <div class="violation">
                <h3>❌ {violation.get('help', 'Unknown Rule').replace("'", "\\'").replace('"', '\\"')}</h3>
                <div class="violation-details">
                    <div class="detail-item">
                        <div class="detail-label">Impact</div>
                        <div class="detail-value">{violation.get('impact', 'Unknown')}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Description</div>
                        <div class="detail-value">{violation.get('description', 'No description').replace("'", "\\'").replace('"', '\\"')}</div>
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
        if current_url is not None:
            violations_js += "</div>"
        
        # Generate JavaScript for passes list with URL grouping
        passes_js = ""
        current_url = None
        for pass_result in all_passes:
            if pass_result.get('url') != current_url:
                if current_url is not None:
                    passes_js += "</div>"
                current_url = pass_result.get('url')
                passes_js += f'<h4 style="color: #22543d; margin: 20px 0 10px 0; padding: 10px; background: #c6f6d5; border-radius: 5px;">🌐 {current_url}</h4><div style="margin-left: 20px;">'
            
            passes_js += f"""
            <div class="pass">
                <h3>✅ {pass_result.get('help', 'Unknown Rule').replace("'", "\\'").replace('"', '\\"')}</h3>
                <div class="pass-details">
                    <div class="detail-item">
                        <div class="detail-label">Description</div>
                        <div class="detail-value">{pass_result.get('description', 'No description').replace("'", "\\'").replace('"', '\\"')}</div>
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
        if current_url is not None:
            passes_js += "</div>"
        
        # Generate JavaScript for URLs list
        urls_js = ""
        for result in results:
            url = result.get('url', 'Unknown URL')
            violations = []
            passes = []
            
            if 'results' in result and result['results']:
                violations = result['results'].get('violations', [])
                passes = result['results'].get('passes', [])
            
            urls_js += f"""
            <div class="url-item">
                <h4>🌐 {url}</h4>
                <div class="url-item-stats">
                    <div class="url-item-stat violations">{len(violations)} Violations</div>
                    <div class="url-item-stat passes">{len(passes)} Passes</div>
                </div>
            </div>
            """
        
        # Generate JavaScript for errors list
        errors_js = ""
        for result in results:
            url = result.get('url', 'Unknown URL')
            
            if 'error' in result and result['error']:
                errors_js += f"""
                <div class="error-item">
                    <h4>🌐 {url}</h4>
                    <div class="error-message">{result['error']}</div>
                </div>
                """
        
        # If no errors, show a message
        if not errors_js:
            errors_js = """
            <div class="error-item">
                <h4>✅ No Test Errors</h4>
                <div class="error-message">All tests completed successfully without any errors.</div>
            </div>
            """
        
        html += f"""
        </div>
    </div>
    
    <script>
        // Store the content for each section
        const violationsContent = `{violations_js}`;
        const passesContent = `{passes_js}`;
        const urlsContent = `{urls_js}`;
        const errorsContent = `{errors_js}`;
        
        function showViolations() {{
            console.log('showViolations called');
            document.getElementById('violations-details').classList.remove('hidden');
            document.getElementById('passes-details').classList.add('hidden');
            document.getElementById('urls-details').classList.add('hidden');
            document.getElementById('errors-details').classList.add('hidden');
            document.getElementById('results-section').classList.add('hidden');
            document.getElementById('violations-list').innerHTML = violationsContent;
        }}
        
        function showPasses() {{
            console.log('showPasses called');
            document.getElementById('passes-details').classList.remove('hidden');
            document.getElementById('violations-details').classList.add('hidden');
            document.getElementById('urls-details').classList.add('hidden');
            document.getElementById('errors-details').classList.add('hidden');
            document.getElementById('results-section').classList.add('hidden');
            document.getElementById('passes-list').innerHTML = passesContent;
        }}
        
        function showUrls() {{
            console.log('showUrls called');
            document.getElementById('urls-details').classList.remove('hidden');
            document.getElementById('violations-details').classList.add('hidden');
            document.getElementById('passes-details').classList.add('hidden');
            document.getElementById('errors-details').classList.add('hidden');
            document.getElementById('results-section').classList.add('hidden');
            document.getElementById('urls-list').innerHTML = urlsContent;
        }}

        function showErrors() {{
            console.log('showErrors called');
            document.getElementById('errors-details').classList.remove('hidden');
            document.getElementById('violations-details').classList.add('hidden');
            document.getElementById('passes-details').classList.add('hidden');
            document.getElementById('urls-details').classList.add('hidden');
            document.getElementById('results-section').classList.remove('hidden');
            document.getElementById('errors-list').innerHTML = errorsContent;
        }}
        
        function hideViolations() {{
            console.log('hideViolations called');
            document.getElementById('violations-details').classList.add('hidden');
            document.getElementById('results-section').classList.remove('hidden');
        }}
        
        function hidePasses() {{
            console.log('hidePasses called');
            document.getElementById('passes-details').classList.add('hidden');
            document.getElementById('results-section').classList.remove('hidden');
        }}

        function hideUrls() {{
            console.log('hideUrls called');
            document.getElementById('urls-details').classList.add('hidden');
            document.getElementById('results-section').classList.remove('hidden');
        }}

        function hideErrors() {{
            console.log('hideErrors called');
            document.getElementById('errors-details').classList.add('hidden');
            document.getElementById('results-section').classList.remove('hidden');
        }}
        
        // Add event listeners as backup
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('DOM loaded, adding event listeners');
            
            // Add click event listeners to metric cards
            const violationsCard = document.querySelector('.metric-card.violations');
            const passesCard = document.querySelector('.metric-card.passes');
            const urlsCard = document.querySelector('.metric-card.urls');
            const errorsCard = document.querySelector('.metric-card.errors');
            
            if (violationsCard) {{
                violationsCard.addEventListener('click', showViolations);
                console.log('Added click listener to violations card');
            }}
            
            if (passesCard) {{
                passesCard.addEventListener('click', showPasses);
                console.log('Added click listener to passes card');
            }}
            
            if (urlsCard) {{
                urlsCard.addEventListener('click', showUrls);
                console.log('Added click listener to urls card');
            }}
            
            if (errorsCard) {{
                errorsCard.addEventListener('click', showErrors);
                console.log('Added click listener to errors card');
            }}
        }});
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