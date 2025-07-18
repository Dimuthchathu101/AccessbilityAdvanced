"""
Tenon.io API integration for accessibility testing.

This module provides integration with the Tenon.io API for
comprehensive accessibility testing.
"""

import requests
import logging
import time
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse


class TenonClient:
    """Client for Tenon.io accessibility testing API."""
    
    def __init__(self, api_key: str, base_url: str = "https://tenon.io/api/"):
        """Initialize the TenonClient.
        
        Args:
            api_key: Tenon.io API key
            base_url: Base URL for Tenon API
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.logger = logging.getLogger(__name__)
        
    def test_url(self, url: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Test a URL for accessibility issues.
        
        Args:
            url: URL to test
            options: Additional testing options
            
        Returns:
            Dictionary containing test results
        """
        if not options:
            options = {}
        
        payload = {
            'key': self.api_key,
            'url': url,
            **options
        }
        
        try:
            self.logger.info(f"Testing URL with Tenon: {url}")
            response = requests.post(f"{self.base_url}/index.php", data=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # Add metadata
            result['metadata'] = {
                'url': url,
                'timestamp': self._get_timestamp(),
                'api_version': 'tenon.io'
            }
            
            return result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error testing {url} with Tenon: {str(e)}")
            return {
                'error': str(e),
                'metadata': {
                    'url': url,
                    'timestamp': self._get_timestamp(),
                    'api_version': 'tenon.io'
                }
            }
    
    def test_html(self, html_content: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Test HTML content for accessibility issues.
        
        Args:
            html_content: HTML content to test
            options: Additional testing options
            
        Returns:
            Dictionary containing test results
        """
        if not options:
            options = {}
        
        payload = {
            'key': self.api_key,
            'src': html_content,
            **options
        }
        
        try:
            self.logger.info("Testing HTML content with Tenon")
            response = requests.post(f"{self.base_url}/index.php", data=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # Add metadata
            result['metadata'] = {
                'content_type': 'html',
                'timestamp': self._get_timestamp(),
                'api_version': 'tenon.io'
            }
            
            return result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error testing HTML with Tenon: {str(e)}")
            return {
                'error': str(e),
                'metadata': {
                    'content_type': 'html',
                    'timestamp': self._get_timestamp(),
                    'api_version': 'tenon.io'
                }
            }
    
    def get_test_status(self, test_id: str) -> Dict[str, Any]:
        """Get the status of a test by ID.
        
        Args:
            test_id: Test ID from a previous test request
            
        Returns:
            Dictionary containing test status
        """
        payload = {
            'key': self.api_key,
            'testID': test_id
        }
        
        try:
            response = requests.post(f"{self.base_url}/index.php", data=payload)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting test status for {test_id}: {str(e)}")
            return {'error': str(e)}
    
    def wait_for_test_completion(self, test_id: str, max_wait: int = 300) -> Dict[str, Any]:
        """Wait for a test to complete and return results.
        
        Args:
            test_id: Test ID to wait for
            max_wait: Maximum time to wait in seconds
            
        Returns:
            Dictionary containing test results
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status = self.get_test_status(test_id)
            
            if 'error' in status:
                return status
            
            if status.get('status') == 'complete':
                return status
            
            # Wait before checking again
            time.sleep(5)
        
        return {'error': f'Test {test_id} did not complete within {max_wait} seconds'}
    
    def get_available_tests(self) -> Dict[str, Any]:
        """Get list of available tests from Tenon.
        
        Returns:
            Dictionary containing available tests
        """
        payload = {
            'key': self.api_key,
            'action': 'tests'
        }
        
        try:
            response = requests.post(f"{self.base_url}/index.php", data=payload)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting available tests: {str(e)}")
            return {'error': str(e)}
    
    def get_test_metadata(self, test_id: str) -> Dict[str, Any]:
        """Get metadata for a specific test.
        
        Args:
            test_id: Test ID to get metadata for
            
        Returns:
            Dictionary containing test metadata
        """
        payload = {
            'key': self.api_key,
            'action': 'metadata',
            'testID': test_id
        }
        
        try:
            response = requests.post(f"{self.base_url}/index.php", data=payload)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting test metadata for {test_id}: {str(e)}")
            return {'error': str(e)}
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def validate_api_key(self) -> bool:
        """Validate the API key by making a simple request.
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            # Try to get available tests as a validation check
            result = self.get_available_tests()
            return 'error' not in result
        except Exception:
            return False
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics.
        
        Returns:
            Dictionary containing usage statistics
        """
        payload = {
            'key': self.api_key,
            'action': 'usage'
        }
        
        try:
            response = requests.post(f"{self.base_url}/index.php", data=payload)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting usage stats: {str(e)}")
            return {'error': str(e)} 