"""
Axe-core integration for accessibility testing.

This module provides integration with axe-core to run automated
accessibility tests on web pages.
"""

import json
import logging
import os
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
        self.axe_loaded = False
        
    def setup_driver(self) -> webdriver.Chrome:
        """Set up Chrome WebDriver with axe-core injection."""
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=options)
        return self.driver
    
    def _load_axe_core(self):
        """Load axe-core JavaScript library into the page."""
        try:
            # Get the path to axe.min.js
            current_dir = os.path.dirname(os.path.abspath(__file__))
            axe_path = os.path.join(current_dir, 'axe.min.js')
            
            # Read and inject axe-core
            with open(axe_path, 'r', encoding='utf-8') as f:
                axe_script = f.read()
            
            # Inject axe-core into the page
            self.driver.execute_script(axe_script)
            self.logger.info("Axe-core library loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load axe-core: {str(e)}")
            raise
    
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
            
            # Load axe-core for each URL (since page context changes)
            self._load_axe_core()
            
            # Prepare options for axe-core
            options = {}
            if rules:
                options["rules"] = {rule: {"enabled": True} for rule in rules}
            
            # Run axe-core tests with proper JavaScript execution
            result = self.driver.execute_async_script("""
                var options = arguments[0];
                var callback = arguments[arguments.length - 1];
                
                if (typeof axe === 'undefined') {
                    callback({
                        error: 'Axe-core library not loaded',
                        results: null
                    });
                    return;
                }
                
                axe.run(options, (err, results) => {
                    callback({
                        error: err ? err.message : null,
                        results: results
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
            self.axe_loaded = False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 