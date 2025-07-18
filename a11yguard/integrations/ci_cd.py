"""
CI/CD helpers for accessibility testing.

This module provides utilities for integrating accessibility testing
into continuous integration and deployment pipelines.
"""

import os
import sys
import logging
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class CICDHelper:
    """Helper class for CI/CD integration of accessibility testing."""
    
    def __init__(self):
        """Initialize the CICDHelper."""
        self.logger = logging.getLogger(__name__)
        self.ci_platform = self._detect_ci_platform()
        
    def _detect_ci_platform(self) -> str:
        """Detect the current CI/CD platform."""
        if os.getenv('GITHUB_ACTIONS'):
            return 'github_actions'
        elif os.getenv('GITLAB_CI'):
            return 'gitlab_ci'
        elif os.getenv('JENKINS_URL'):
            return 'jenkins'
        elif os.getenv('TRAVIS'):
            return 'travis'
        elif os.getenv('CIRCLECI'):
            return 'circleci'
        else:
            return 'unknown'
    
    def get_ci_environment(self) -> Dict[str, Any]:
        """Get information about the current CI environment.
        
        Returns:
            Dictionary containing CI environment information
        """
        env_info = {
            'platform': self.ci_platform,
            'build_id': self._get_build_id(),
            'branch': self._get_branch_name(),
            'commit': self._get_commit_hash(),
            'pull_request': self._get_pull_request_info(),
            'workspace': os.getcwd()
        }
        
        return env_info
    
    def _get_build_id(self) -> Optional[str]:
        """Get the current build ID."""
        if self.ci_platform == 'github_actions':
            return os.getenv('GITHUB_RUN_ID')
        elif self.ci_platform == 'gitlab_ci':
            return os.getenv('CI_PIPELINE_ID')
        elif self.ci_platform == 'jenkins':
            return os.getenv('BUILD_NUMBER')
        elif self.ci_platform == 'travis':
            return os.getenv('TRAVIS_BUILD_NUMBER')
        elif self.ci_platform == 'circleci':
            return os.getenv('CIRCLE_BUILD_NUM')
        return None
    
    def _get_branch_name(self) -> Optional[str]:
        """Get the current branch name."""
        if self.ci_platform == 'github_actions':
            return os.getenv('GITHUB_REF_NAME')
        elif self.ci_platform == 'gitlab_ci':
            return os.getenv('CI_COMMIT_REF_NAME')
        elif self.ci_platform == 'jenkins':
            return os.getenv('GIT_BRANCH')
        elif self.ci_platform == 'travis':
            return os.getenv('TRAVIS_BRANCH')
        elif self.ci_platform == 'circleci':
            return os.getenv('CIRCLE_BRANCH')
        return None
    
    def _get_commit_hash(self) -> Optional[str]:
        """Get the current commit hash."""
        if self.ci_platform == 'github_actions':
            return os.getenv('GITHUB_SHA')
        elif self.ci_platform == 'gitlab_ci':
            return os.getenv('CI_COMMIT_SHA')
        elif self.ci_platform == 'jenkins':
            return os.getenv('GIT_COMMIT')
        elif self.ci_platform == 'travis':
            return os.getenv('TRAVIS_COMMIT')
        elif self.ci_platform == 'circleci':
            return os.getenv('CIRCLE_SHA1')
        return None
    
    def _get_pull_request_info(self) -> Optional[Dict[str, str]]:
        """Get pull request information."""
        if self.ci_platform == 'github_actions':
            pr_number = os.getenv('GITHUB_EVENT_NAME') == 'pull_request'
            if pr_number:
                return {
                    'number': os.getenv('GITHUB_EVENT_NUMBER'),
                    'title': os.getenv('GITHUB_EVENT_HEAD_REF')
                }
        elif self.ci_platform == 'gitlab_ci':
            mr_id = os.getenv('CI_MERGE_REQUEST_ID')
            if mr_id:
                return {
                    'number': mr_id,
                    'title': os.getenv('CI_MERGE_REQUEST_TITLE', '')
                }
        return None
    
    def set_ci_output(self, key: str, value: str):
        """Set CI output variable.
        
        Args:
            key: Output key
            value: Output value
        """
        if self.ci_platform == 'github_actions':
            # GitHub Actions uses a special file for outputs
            output_file = os.getenv('GITHUB_OUTPUT')
            if output_file:
                with open(output_file, 'a') as f:
                    f.write(f"{key}={value}\n")
        elif self.ci_platform == 'gitlab_ci':
            # GitLab CI uses echo to set variables
            print(f"::set-output name={key}::{value}")
        else:
            # For other platforms, just print
            print(f"CI_OUTPUT_{key}={value}")
    
    def create_ci_summary(self, test_results: List[Dict[str, Any]]) -> str:
        """Create a summary for CI platforms that support it.
        
        Args:
            test_results: List of test results
            
        Returns:
            Summary string
        """
        total_tests = len(test_results)
        total_violations = 0
        total_errors = 0
        
        for result in test_results:
            if 'error' in result:
                total_errors += 1
            elif 'results' in result and result['results']:
                violations = result['results'].get('violations', [])
                total_violations += len(violations)
        
        summary = f"""
## Accessibility Test Results

- **URLs Tested:** {total_tests}
- **Total Violations:** {total_violations}
- **Test Errors:** {total_errors}
- **Status:** {'❌ Failed' if total_violations > 0 or total_errors > 0 else '✅ Passed'}
        """
        
        return summary.strip()
    
    def should_fail_build(self, test_results: List[Dict[str, Any]], 
                         max_violations: int = 0) -> bool:
        """Determine if the build should fail based on test results.
        
        Args:
            test_results: List of test results
            max_violations: Maximum allowed violations before failing
            
        Returns:
            True if build should fail, False otherwise
        """
        total_violations = 0
        total_errors = 0
        
        for result in test_results:
            if 'error' in result:
                total_errors += 1
            elif 'results' in result and result['results']:
                violations = result['results'].get('violations', [])
                total_violations += len(violations)
        
        return total_violations > max_violations or total_errors > 0
    
    def run_accessibility_tests(self, urls: List[str], 
                               config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Run accessibility tests and handle CI integration.
        
        Args:
            urls: List of URLs to test
            config: Test configuration
            
        Returns:
            List of test results
        """
        from ..core.axe_runner import AxeRunner
        from ..core.reporter import ReportGenerator
        
        if not config:
            config = {}
        
        results = []
        
        try:
            with AxeRunner(headless=True) as runner:
                for url in urls:
                    self.logger.info(f"Testing URL: {url}")
                    result = runner.run_test(url, config.get('rules'))
                    results.append(result)
                    
                    # Log progress for CI
                    if self.ci_platform != 'unknown':
                        print(f"Tested: {url}")
        
        except Exception as e:
            self.logger.error(f"Error running accessibility tests: {str(e)}")
            # Add error result for each URL
            for url in urls:
                results.append({
                    'url': url,
                    'error': str(e),
                    'timestamp': self._get_timestamp()
                })
        
        return results
    
    def generate_ci_reports(self, test_results: List[Dict[str, Any]], 
                           output_dir: str = "outputs/reports") -> Dict[str, str]:
        """Generate reports suitable for CI platforms.
        
        Args:
            test_results: List of test results
            output_dir: Directory to save reports
            
        Returns:
            Dictionary mapping report types to file paths
        """
        from ..core.reporter import ReportGenerator
        
        reporter = ReportGenerator(output_dir)
        reports = {}
        
        # Generate different report formats
        reports['json'] = reporter.generate_json_report(test_results)
        reports['html'] = reporter.generate_html_report(test_results)
        reports['markdown'] = reporter.generate_markdown_report(test_results)
        
        # Create CI-specific summary
        if self.ci_platform == 'github_actions':
            summary = self.create_ci_summary(test_results)
            summary_path = Path(output_dir) / "ci_summary.md"
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(summary_path, 'w') as f:
                f.write(summary)
            reports['ci_summary'] = str(summary_path)
        
        return reports
    
    def upload_artifacts(self, file_paths: List[str], 
                        artifact_name: str = "accessibility-reports"):
        """Upload test artifacts to CI platform.
        
        Args:
            file_paths: List of file paths to upload
            artifact_name: Name for the artifact collection
        """
        if self.ci_platform == 'github_actions':
            # GitHub Actions uses actions/upload-artifact
            for file_path in file_paths:
                if Path(file_path).exists():
                    print(f"Would upload: {file_path}")
                    # In a real implementation, you'd use the GitHub Actions API
        elif self.ci_platform == 'gitlab_ci':
            # GitLab CI artifacts are configured in .gitlab-ci.yml
            print(f"Artifacts would be uploaded: {file_paths}")
        else:
            print(f"Artifacts available: {file_paths}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def create_github_issue_comment(self, test_results: List[Dict[str, Any]], 
                                   issue_number: Optional[str] = None) -> str:
        """Create a comment for GitHub issues/PRs.
        
        Args:
            test_results: List of test results
            issue_number: Issue/PR number (optional)
            
        Returns:
            Comment content
        """
        summary = self.create_ci_summary(test_results)
        
        comment = f"""
{summary}

<details>
<summary>Detailed Results</summary>

"""
        
        for result in test_results:
            url = result.get('url', 'Unknown URL')
            comment += f"\n### {url}\n\n"
            
            if 'error' in result:
                comment += f"❌ **Error:** {result['error']}\n\n"
                continue
            
            if 'results' in result and result['results']:
                violations = result['results'].get('violations', [])
                passes = result['results'].get('passes', [])
                
                if violations:
                    comment += "#### Violations\n\n"
                    for violation in violations:
                        comment += f"- **{violation.get('help', 'Unknown Rule')}** ({violation.get('impact', 'Unknown')})\n"
                        comment += f"  - {violation.get('description', 'No description')}\n\n"
                
                if passes:
                    comment += f"#### Passes ({len(passes)})\n\n"
                    comment += "✅ All accessibility checks passed for this section.\n\n"
        
        comment += "</details>"
        
        return comment 