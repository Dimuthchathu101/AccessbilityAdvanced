"""
Static HTML/ARIA analyzer for accessibility validation.

This module provides static analysis of HTML content to identify
potential accessibility issues without requiring a browser.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class AccessibilityIssue:
    """Represents an accessibility issue found during static analysis."""
    rule_id: str
    severity: str  # 'error', 'warning', 'info'
    message: str
    element: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    suggestion: Optional[str] = None


class StaticAnalyzer:
    """Static analyzer for HTML/ARIA accessibility validation."""
    
    def __init__(self):
        """Initialize the StaticAnalyzer."""
        self.logger = logging.getLogger(__name__)
        self.issues: List[AccessibilityIssue] = []
        
    def analyze_html(self, html_content: str) -> List[AccessibilityIssue]:
        """Analyze HTML content for accessibility issues.
        
        Args:
            html_content: Raw HTML content to analyze
            
        Returns:
            List of accessibility issues found
        """
        self.issues = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Run various checks
            self._check_missing_alt_text(soup)
            self._check_missing_landmarks(soup)
            self._check_form_labels(soup)
            self._check_heading_structure(soup)
            self._check_color_contrast_attributes(soup)
            self._check_aria_attributes(soup)
            self._check_keyboard_navigation(soup)
            
        except Exception as e:
            self.logger.error(f"Error analyzing HTML: {str(e)}")
            self.issues.append(AccessibilityIssue(
                rule_id="PARSE_ERROR",
                severity="error",
                message=f"Failed to parse HTML: {str(e)}",
                element="document"
            ))
        
        return self.issues
    
    def _check_missing_alt_text(self, soup: BeautifulSoup):
        """Check for images without alt text."""
        images = soup.find_all('img')
        for img in images:
            if not img.get('alt'):
                self.issues.append(AccessibilityIssue(
                    rule_id="IMG_MISSING_ALT",
                    severity="error",
                    message="Image missing alt text",
                    element=str(img)[:100],
                    suggestion="Add descriptive alt text to the image"
                ))
    
    def _check_missing_landmarks(self, soup: BeautifulSoup):
        """Check for missing landmark elements."""
        landmarks = soup.find_all(['header', 'nav', 'main', 'aside', 'footer'])
        if not landmarks:
            self.issues.append(AccessibilityIssue(
                rule_id="MISSING_LANDMARKS",
                severity="warning",
                message="No landmark elements found",
                element="document",
                suggestion="Add semantic landmark elements (header, nav, main, etc.)"
            ))
    
    def _check_form_labels(self, soup: BeautifulSoup):
        """Check for form controls without proper labels."""
        form_controls = soup.find_all(['input', 'select', 'textarea'])
        for control in form_controls:
            control_id = control.get('id')
            if control_id:
                label = soup.find('label', attrs={'for': control_id})
                if not label:
                    self.issues.append(AccessibilityIssue(
                        rule_id="FORM_CONTROL_NO_LABEL",
                        severity="error",
                        message=f"Form control with id '{control_id}' has no associated label",
                        element=str(control)[:100],
                        suggestion="Add a label element with 'for' attribute matching the control's id"
                    ))
    
    def _check_heading_structure(self, soup: BeautifulSoup):
        """Check for proper heading hierarchy."""
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if not headings:
            self.issues.append(AccessibilityIssue(
                rule_id="NO_HEADINGS",
                severity="warning",
                message="No heading elements found",
                element="document",
                suggestion="Add heading elements to provide document structure"
            ))
            return
        
        # Check for skipped heading levels
        heading_levels = [int(h.name[1]) for h in headings]
        for i in range(len(heading_levels) - 1):
            if heading_levels[i + 1] - heading_levels[i] > 1:
                self.issues.append(AccessibilityIssue(
                    rule_id="SKIPPED_HEADING_LEVEL",
                    severity="warning",
                    message=f"Heading level skipped from h{heading_levels[i]} to h{heading_levels[i + 1]}",
                    element=str(headings[i + 1])[:100],
                    suggestion="Use sequential heading levels (h1, h2, h3, etc.)"
                ))
    
    def _check_color_contrast_attributes(self, soup: BeautifulSoup):
        """Check for elements that might have color contrast issues."""
        # This is a basic check - in practice, you'd need to analyze CSS
        elements_with_color = soup.find_all(style=True)
        for element in elements_with_color:
            style = element.get('style', '')
            if 'color:' in style and 'background-color:' not in style:
                self.issues.append(AccessibilityIssue(
                    rule_id="POTENTIAL_CONTRAST_ISSUE",
                    severity="info",
                    message="Element has color but no background-color specified",
                    element=str(element)[:100],
                    suggestion="Ensure sufficient color contrast ratio (4.5:1 for normal text)"
                ))
    
    def _check_aria_attributes(self, soup: BeautifulSoup):
        """Check for invalid or missing ARIA attributes."""
        # Check for elements with role but no accessible name
        elements_with_role = soup.find_all(attrs={'role': True})
        for element in elements_with_role:
            role = element.get('role')
            aria_label = element.get('aria-label')
            aria_labelledby = element.get('aria-labelledby')
            
            if not (aria_label or aria_labelledby):
                # Some roles don't require labels
                if role not in ['presentation', 'none', 'banner', 'contentinfo']:
                    self.issues.append(AccessibilityIssue(
                        rule_id="ARIA_ROLE_NO_LABEL",
                        severity="warning",
                        message=f"Element with role '{role}' has no accessible name",
                        element=str(element)[:100],
                        suggestion="Add aria-label or aria-labelledby attribute"
                    ))
    
    def _check_keyboard_navigation(self, soup: BeautifulSoup):
        """Check for keyboard navigation issues."""
        # Check for clickable elements without keyboard support
        clickable_elements = soup.find_all(['button', 'a', 'input'])
        for element in clickable_elements:
            if element.name == 'a' and not element.get('href'):
                self.issues.append(AccessibilityIssue(
                    rule_id="LINK_NO_HREF",
                    severity="error",
                    message="Link element has no href attribute",
                    element=str(element)[:100],
                    suggestion="Add href attribute or use button element instead"
                ))
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the analysis results."""
        severity_counts = {}
        for issue in self.issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        
        return {
            "total_issues": len(self.issues),
            "severity_breakdown": severity_counts,
            "has_errors": severity_counts.get("error", 0) > 0,
            "has_warnings": severity_counts.get("warning", 0) > 0
        } 