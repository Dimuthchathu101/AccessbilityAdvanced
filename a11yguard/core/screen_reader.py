"""
Screen reader helpers for accessibility testing.

This module provides utilities for testing screen reader compatibility
and generating screen reader-friendly content.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ScreenReaderElement:
    """Represents an element as it would be announced by a screen reader."""
    tag_name: str
    accessible_name: str
    role: Optional[str] = None
    state: Optional[str] = None
    description: Optional[str] = None
    position: Optional[str] = None


class ScreenReaderHelper:
    """Helper class for screen reader accessibility testing."""
    
    def __init__(self):
        """Initialize the ScreenReaderHelper."""
        self.logger = logging.getLogger(__name__)
        
    def generate_announcement_text(self, element_data: Dict[str, Any]) -> str:
        """Generate how an element would be announced by a screen reader.
        
        Args:
            element_data: Dictionary containing element information
            
        Returns:
            String representing the screen reader announcement
        """
        parts = []
        
        # Add accessible name
        if element_data.get('accessible_name'):
            parts.append(element_data['accessible_name'])
        
        # Add role
        role = element_data.get('role')
        if role and role not in ['text', 'generic']:
            parts.append(f"({role})")
        
        # Add state
        state = element_data.get('state')
        if state:
            parts.append(state)
        
        # Add description
        description = element_data.get('description')
        if description:
            parts.append(description)
        
        # Add position information
        position = element_data.get('position')
        if position:
            parts.append(position)
        
        return " ".join(parts) if parts else "Unnamed element"
    
    def validate_focus_order(self, focusable_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate logical focus order of elements.
        
        Args:
            focusable_elements: List of focusable elements with their order
            
        Returns:
            List of focus order issues found
        """
        issues = []
        
        for i, element in enumerate(focusable_elements):
            # Check for missing accessible names
            if not element.get('accessible_name'):
                issues.append({
                    'type': 'missing_name',
                    'element': element.get('tag_name', 'unknown'),
                    'position': i + 1,
                    'message': 'Focusable element has no accessible name'
                })
            
            # Check for logical order issues (basic checks)
            if i > 0:
                prev_element = focusable_elements[i - 1]
                
                # Check for heading level jumps
                if (element.get('tag_name', '').startswith('h') and 
                    prev_element.get('tag_name', '').startswith('h')):
                    current_level = int(element['tag_name'][1])
                    prev_level = int(prev_element['tag_name'][1])
                    
                    if current_level - prev_level > 1:
                        issues.append({
                            'type': 'heading_jump',
                            'element': element.get('tag_name', 'unknown'),
                            'position': i + 1,
                            'message': f'Heading level jumps from h{prev_level} to h{current_level}'
                        })
        
        return issues
    
    def check_skip_links(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check for proper skip link implementation.
        
        Args:
            elements: List of page elements
            
        Returns:
            Dictionary with skip link analysis
        """
        skip_links = [e for e in elements if self._is_skip_link(e)]
        
        analysis = {
            'has_skip_links': len(skip_links) > 0,
            'skip_link_count': len(skip_links),
            'issues': []
        }
        
        if not skip_links:
            analysis['issues'].append({
                'type': 'no_skip_links',
                'message': 'No skip links found for keyboard navigation'
            })
        else:
            # Check if skip links are properly implemented
            for link in skip_links:
                target_id = link.get('href', '').lstrip('#')
                if not target_id:
                    analysis['issues'].append({
                        'type': 'invalid_skip_link',
                        'element': link.get('tag_name', 'unknown'),
                        'message': 'Skip link has no target'
                    })
        
        return analysis
    
    def _is_skip_link(self, element: Dict[str, Any]) -> bool:
        """Check if an element is a skip link."""
        if element.get('tag_name') != 'a':
            return False
        
        href = element.get('href', '')
        text = element.get('accessible_name', '').lower()
        
        # Check for common skip link patterns
        skip_patterns = ['skip', 'jump', 'go to', 'navigate to']
        return any(pattern in text for pattern in skip_patterns) and href.startswith('#')
    
    def generate_landmark_summary(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of landmark elements.
        
        Args:
            elements: List of page elements
            
        Returns:
            Dictionary with landmark analysis
        """
        landmarks = [e for e in elements if self._is_landmark(e)]
        
        landmark_types = {}
        for landmark in landmarks:
            landmark_type = landmark.get('role') or landmark.get('tag_name')
            if landmark_type not in landmark_types:
                landmark_types[landmark_type] = []
            landmark_types[landmark_type].append(landmark)
        
        return {
            'total_landmarks': len(landmarks),
            'landmark_types': landmark_types,
            'has_main': any(l.get('role') == 'main' or l.get('tag_name') == 'main' for l in landmarks),
            'has_navigation': any(l.get('role') == 'navigation' or l.get('tag_name') == 'nav' for l in landmarks),
            'has_header': any(l.get('role') == 'banner' or l.get('tag_name') == 'header' for l in landmarks),
            'has_footer': any(l.get('role') == 'contentinfo' or l.get('tag_name') == 'footer' for l in landmarks)
        }
    
    def _is_landmark(self, element: Dict[str, Any]) -> bool:
        """Check if an element is a landmark."""
        landmark_roles = ['banner', 'complementary', 'contentinfo', 'form', 'main', 'navigation', 'region', 'search']
        landmark_tags = ['header', 'nav', 'main', 'aside', 'footer']
        
        role = element.get('role')
        tag = element.get('tag_name')
        
        return role in landmark_roles or tag in landmark_tags
    
    def check_aria_live_regions(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for proper ARIA live region implementation.
        
        Args:
            elements: List of page elements
            
        Returns:
            List of live region issues
        """
        issues = []
        live_regions = [e for e in elements if e.get('aria-live')]
        
        for region in live_regions:
            # Check if live region has accessible name
            if not region.get('accessible_name'):
                issues.append({
                    'type': 'live_region_no_name',
                    'element': region.get('tag_name', 'unknown'),
                    'message': 'ARIA live region has no accessible name'
                })
            
            # Check for appropriate live value
            live_value = region.get('aria-live')
            if live_value not in ['polite', 'assertive', 'off']:
                issues.append({
                    'type': 'invalid_live_value',
                    'element': region.get('tag_name', 'unknown'),
                    'value': live_value,
                    'message': 'Invalid aria-live value'
                })
        
        return issues
    
    def generate_screen_reader_report(self, page_elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a comprehensive screen reader accessibility report.
        
        Args:
            page_elements: List of all page elements with accessibility data
            
        Returns:
            Dictionary containing screen reader analysis
        """
        focusable_elements = [e for e in page_elements if e.get('focusable', False)]
        
        return {
            'focus_order_issues': self.validate_focus_order(focusable_elements),
            'skip_link_analysis': self.check_skip_links(page_elements),
            'landmark_summary': self.generate_landmark_summary(page_elements),
            'live_region_issues': self.check_aria_live_regions(page_elements),
            'total_focusable_elements': len(focusable_elements),
            'total_elements': len(page_elements),
            'accessibility_score': self._calculate_accessibility_score(page_elements)
        }
    
    def _calculate_accessibility_score(self, elements: List[Dict[str, Any]]) -> float:
        """Calculate a basic accessibility score for screen reader compatibility."""
        if not elements:
            return 0.0
        
        score = 100.0
        total_elements = len(elements)
        
        # Deduct points for various issues
        for element in elements:
            # Missing accessible names
            if element.get('focusable') and not element.get('accessible_name'):
                score -= 5
            
            # Missing alt text for images
            if element.get('tag_name') == 'img' and not element.get('alt'):
                score -= 10
            
            # Missing form labels
            if element.get('tag_name') in ['input', 'select', 'textarea']:
                if not element.get('label') and not element.get('aria-label'):
                    score -= 8
        
        return max(0.0, score) 