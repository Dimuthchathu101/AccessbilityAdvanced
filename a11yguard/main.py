#!/usr/bin/env python3
"""
a11yguard - Advanced Accessibility Testing Tool

A comprehensive accessibility testing tool that combines automated testing,
static analysis, and reporting to ensure web content meets accessibility standards.
"""

import sys
import logging
import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Import a11yguard modules
from core.axe_runner import AxeRunner
from core.static_analyzer import StaticAnalyzer
from core.reporter import ReportGenerator
from core.screen_reader import ScreenReaderHelper
from integrations.tenon_client import TenonClient
from integrations.ci_cd import CICDHelper
from tests.test_suite import TestSuite
from tests.test_cases.wcag_2_2 import WCAG_TEST_CASES
from tests.test_cases.section_508 import SECTION_508_TEST_CASES


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Rich console
console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="a11yguard")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.pass_context
def cli(ctx, verbose, config):
    """a11yguard - Advanced Accessibility Testing Tool
    
    A comprehensive accessibility testing tool that combines automated testing,
    static analysis, and reporting to ensure web content meets accessibility standards.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load configuration
    ctx.ensure_object(dict)
    ctx.obj['config'] = load_config(config) if config else {}


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        console.print(f"[red]Error loading config: {e}[/red]")
        return {}


@cli.command()
@click.argument('urls', nargs=-1)
@click.option('--urls-file', '-f', type=click.Path(exists=True), help='File containing URLs to test')
@click.option('--output', '-o', default='outputs/reports', help='Output directory for reports')
@click.option('--format', '-fmt', type=click.Choice(['json', 'html', 'csv', 'markdown']), 
              default='html', help='Report format')
@click.option('--headless', is_flag=True, default=True, help='Run browser in headless mode')
@click.option('--rules', '-r', help='Comma-separated list of specific rules to test')
@click.option('--ruleset', help='Predefined ruleset to use')
@click.pass_context
def test(ctx, urls, urls_file, output, format, headless, rules, ruleset):
    """Run accessibility tests on URLs."""
    config = ctx.obj.get('config', {})
    
    # Get URLs to test
    test_urls = list(urls)
    if urls_file:
        with open(urls_file, 'r') as f:
            test_urls.extend([line.strip() for line in f if line.strip()])
    
    if not test_urls:
        console.print("[red]No URLs provided. Use --help for usage information.[/red]")
        sys.exit(1)
    
    # Parse rules
    test_rules = None
    if rules:
        test_rules = [r.strip() for r in rules.split(',')]
    elif ruleset:
        test_rules = get_ruleset_rules(ruleset, config)
    
    console.print(f"[green]Testing {len(test_urls)} URLs for accessibility...[/green]")
    
    # Run tests
    results = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Running accessibility tests...", total=len(test_urls))
        
        with AxeRunner(headless=headless) as runner:
            for url in test_urls:
                progress.update(task, description=f"Testing {url}")
                result = runner.run_test(url, test_rules)
                results.append(result)
                progress.advance(task)
    
    # Generate reports
    console.print(f"[green]Generating {format} report...[/green]")
    reporter = ReportGenerator(output)
    
    if format == 'json':
        report_path = reporter.generate_json_report(results)
    elif format == 'html':
        report_path = reporter.generate_html_report(results)
    elif format == 'csv':
        report_path = reporter.generate_csv_report(results)
    elif format == 'markdown':
        report_path = reporter.generate_markdown_report(results)
    
    console.print(f"[green]Report generated: {report_path}[/green]")
    
    # Display summary
    display_results_summary(results)


@cli.command()
@click.argument('html_file', type=click.Path(exists=True))
@click.option('--output', '-o', default='outputs/reports', help='Output directory for reports')
@click.option('--format', '-fmt', type=click.Choice(['json', 'html', 'csv', 'markdown']), 
              default='html', help='Report format')
@click.pass_context
def analyze(ctx, html_file, output, format):
    """Analyze HTML file for accessibility issues."""
    console.print(f"[green]Analyzing HTML file: {html_file}[/green]")
    
    # Read HTML content
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Run static analysis
    analyzer = StaticAnalyzer()
    issues = analyzer.analyze_html(html_content)
    
    # Convert issues to results format
    results = [{
        'url': html_file,
        'timestamp': get_timestamp(),
        'results': {
            'violations': [issue.__dict__ for issue in issues if issue.severity == 'error'],
            'passes': [],
            'incomplete': [issue.__dict__ for issue in issues if issue.severity == 'warning'],
            'inapplicable': [issue.__dict__ for issue in issues if issue.severity == 'info']
        }
    }]
    
    # Generate reports
    reporter = ReportGenerator(output)
    
    if format == 'json':
        report_path = reporter.generate_json_report(results)
    elif format == 'html':
        report_path = reporter.generate_html_report(results)
    elif format == 'csv':
        report_path = reporter.generate_csv_report(results)
    elif format == 'markdown':
        report_path = reporter.generate_markdown_report(results)
    
    console.print(f"[green]Analysis report generated: {report_path}[/green]")
    
    # Display summary
    display_analysis_summary(issues)


@cli.command()
@click.argument('urls', nargs=-1)
@click.option('--urls-file', '-f', type=click.Path(exists=True), help='File containing URLs to test')
@click.option('--test-suite', '-s', type=click.Choice(['wcag', 'section508', 'all']), 
              default='all', help='Test suite to run')
@click.option('--output', '-o', default='outputs/reports', help='Output directory for reports')
@click.pass_context
def suite(ctx, urls, urls_file, test_suite, output):
    """Run comprehensive test suites."""
    # Get URLs to test
    test_urls = list(urls)
    if urls_file:
        with open(urls_file, 'r') as f:
            test_urls.extend([line.strip() for line in f if line.strip()])
    
    if not test_urls:
        console.print("[red]No URLs provided. Use --help for usage information.[/red]")
        sys.exit(1)
    
    # Create test suite
    suite_name = f"Accessibility Test Suite - {test_suite.upper()}"
    test_suite_obj = TestSuite(suite_name)
    
    # Add test cases based on selection
    if test_suite in ['wcag', 'all']:
        test_suite_obj.add_test_cases(WCAG_TEST_CASES)
    
    if test_suite in ['section508', 'all']:
        test_suite_obj.add_test_cases(SECTION_508_TEST_CASES)
    
    console.print(f"[green]Running {test_suite_obj.name} on {len(test_urls)} URLs...[/green]")
    
    # Run test suite for each URL
    all_results = []
    for url in test_urls:
        console.print(f"[blue]Testing: {url}[/blue]")
        
        # Get HTML content (simplified - in real implementation, you'd fetch the page)
        context = {'url': url, 'html_content': '<html><body>Test content</body></html>'}
        
        # Run test suite
        results = test_suite_obj.run_suite(context)
        all_results.extend(results)
    
    # Export results
    timestamp = get_timestamp().replace(':', '-')
    export_path = test_suite_obj.export_results('html', f"{output}/test_suite_{timestamp}.html")
    
    console.print(f"[green]Test suite results exported: {export_path}[/green]")
    
    # Display summary
    summary = test_suite_obj.get_results_summary()
    display_test_suite_summary(summary)


@cli.command()
@click.option('--api-key', envvar='TENON_API_KEY', help='Tenon.io API key')
@click.option('--urls-file', '-f', type=click.Path(exists=True), help='File containing URLs to test')
@click.option('--output', '-o', default='outputs/reports', help='Output directory for reports')
@click.pass_context
def tenon(ctx, api_key, urls_file, output):
    """Run tests using Tenon.io API."""
    if not api_key:
        console.print("[red]Tenon.io API key required. Set TENON_API_KEY environment variable or use --api-key.[/red]")
        sys.exit(1)
    
    # Get URLs to test
    test_urls = []
    if urls_file:
        with open(urls_file, 'r') as f:
            test_urls = [line.strip() for line in f if line.strip()]
    
    if not test_urls:
        console.print("[red]No URLs provided. Use --urls-file to specify URLs.[/red]")
        sys.exit(1)
    
    console.print(f"[green]Testing {len(test_urls)} URLs with Tenon.io...[/green]")
    
    # Initialize Tenon client
    tenon_client = TenonClient(api_key)
    
    # Test URLs
    results = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Running Tenon.io tests...", total=len(test_urls))
        
        for url in test_urls:
            progress.update(task, description=f"Testing {url}")
            result = tenon_client.test_url(url)
            results.append(result)
            progress.advance(task)
    
    # Generate reports
    reporter = ReportGenerator(output)
    report_path = reporter.generate_html_report(results)
    
    console.print(f"[green]Tenon.io report generated: {report_path}[/green]")
    
    # Display summary
    display_results_summary(results)


@cli.command()
@click.option('--urls-file', '-f', type=click.Path(exists=True), help='File containing URLs to test')
@click.option('--max-violations', default=0, help='Maximum violations before failing build')
@click.option('--output', '-o', default='outputs/reports', help='Output directory for reports')
@click.pass_context
def ci(ctx, urls_file, max_violations, output):
    """Run tests in CI/CD environment."""
    # Get URLs to test
    test_urls = []
    if urls_file:
        with open(urls_file, 'r') as f:
            test_urls = [line.strip() for line in f if line.strip()]
    
    if not test_urls:
        console.print("[red]No URLs provided. Use --urls-file to specify URLs.[/red]")
        sys.exit(1)
    
    # Initialize CI/CD helper
    ci_helper = CICDHelper()
    
    # Get CI environment info
    env_info = ci_helper.get_ci_environment()
    console.print(f"[blue]CI Environment: {env_info['platform']}[/blue]")
    
    # Run tests
    console.print(f"[green]Running accessibility tests in CI environment...[/green]")
    results = ci_helper.run_accessibility_tests(test_urls)
    
    # Generate CI reports
    reports = ci_helper.generate_ci_reports(results, output)
    
    # Check if build should fail
    should_fail = ci_helper.should_fail_build(results, max_violations)
    
    if should_fail:
        console.print("[red]Build failed due to accessibility violations![/red]")
        sys.exit(1)
    else:
        console.print("[green]Build passed accessibility checks![/green]")
    
    # Display summary
    display_results_summary(results)


def get_ruleset_rules(ruleset_name: str, config: Dict[str, Any]) -> List[str]:
    """Get rules for a specific ruleset."""
    # This would load from the rulesets.yaml configuration
    # For now, return some common rules
    common_rules = [
        'color-contrast',
        'image-alt',
        'label',
        'link-name',
        'page-has-heading-one'
    ]
    return common_rules


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    from datetime import datetime
    return datetime.now().isoformat()


def display_results_summary(results: List[Dict[str, Any]]):
    """Display a summary of test results."""
    total_violations = 0
    total_errors = 0
    
    for result in results:
        if 'error' in result and result['error']:
            total_errors += 1
        elif 'results' in result and result['results']:
            violations = result['results'].get('violations', [])
            total_violations += len(violations)
    
    table = Table(title="Accessibility Test Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="magenta")
    
    table.add_row("URLs Tested", str(len(results)))
    table.add_row("Total Violations", str(total_violations))
    table.add_row("Test Errors", str(total_errors))
    
    console.print(table)


def display_analysis_summary(issues: List[Any]):
    """Display a summary of static analysis results."""
    severity_counts = {}
    for issue in issues:
        severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
    
    table = Table(title="Static Analysis Summary")
    table.add_column("Severity", style="cyan")
    table.add_column("Count", style="magenta")
    
    for severity, count in severity_counts.items():
        table.add_row(severity.title(), str(count))
    
    console.print(table)


def display_test_suite_summary(summary: Dict[str, Any]):
    """Display a summary of test suite results."""
    table = Table(title="Test Suite Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="magenta")
    
    table.add_row("Total Tests", str(summary['total_tests']))
    table.add_row("Passed", str(summary['passed']))
    table.add_row("Failed", str(summary['failed']))
    table.add_row("Errors", str(summary['errors']))
    table.add_row("Skipped", str(summary['skipped']))
    table.add_row("Success Rate", f"{summary['success_rate']}%")
    
    console.print(table)


if __name__ == '__main__':
    cli()