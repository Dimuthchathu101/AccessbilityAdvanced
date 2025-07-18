"""
Axe-core integration for accessibility testing.

This module provides integration with axe-core to run automated
accessibility tests on web pages.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class AxeRunner:
    """Runs axe-core accessibility tests on web pages."""
    
    def __init__(self, headless: bool = True):
        """Initialize the AxeRunner.
        
        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self.driver = None
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self) -> webdriver.Chrome:
        """Set up Chrome WebDriver with axe-core injection."""
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=options)
        
        # Inject axe-core script
        axe_script = self._get_axe_script()
        self.driver.execute_script(axe_script)
        
        return self.driver
    
    def _get_axe_script(self) -> str:
        """Get the axe-core JavaScript code."""
        # In a real implementation, this would load from a CDN or local file
        return """
        // Placeholder for axe-core script injection
        // In production, this would load the actual axe-core library
        window.axe = {
            run: function(context, options, callback) {
                // Mock implementation
                callback(null, {
                    violations: [],
                    passes: [],
                    incomplete: [],
                    inapplicable: []
                });
            }
        };
        """
    
    def run_test(self, url: str, rules: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run accessibility tests on a given URL.
        
        Args:
            url: The URL to test
            rules: Specific rules to run (None for all rules)
            
        Returns:
            Dictionary containing test results
        """
        try:
            if not self.driver:
                self.setup_driver()
            
            self.logger.info(f"Testing accessibility for: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Run axe-core tests
            options = {}
            if rules:
                options["rules"] = {rule: {"enabled": True} for rule in rules}
            
            result = self.driver.execute_script("""
                return new Promise((resolve) => {
                    axe.run(options, (err, results) => {
                        resolve({error: err, results: results});
                    });
                });
            """, options)
            
            return {
                "url": url,
                "timestamp": self._get_timestamp(),
                "results": result.get("results", {}),
                "error": result.get("error")
            }
            
        except Exception as e:
            self.logger.error(f"Error testing {url}: {str(e)}")
            return {
                "url": url,
                "timestamp": self._get_timestamp(),
                "error": str(e)
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 