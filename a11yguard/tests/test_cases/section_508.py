"""
Section 508 test cases for federal accessibility compliance.

This module contains test cases based on Section 508 of the
Rehabilitation Act for federal agencies and contractors.
"""

import logging
from typing import Dict, List, Any, Optional
from ..test_suite import TestCase


def test_equivalent_alternatives(context: Dict[str, Any]) -> Dict[str, Any]:
    """Test §1194.22(a): Text equivalent for non-text elements."""
    html_content = context.get('html_content', '')
    
    if not html_content:
        return {
            'status': 'skipped',
            'message': 'No HTML content provided for testing'
        }
    
    from ...core.static_analyzer import StaticAnalyzer
    
    analyzer = StaticAnalyzer()
    issues = analyzer.analyze_html(html_content)
    
    # Filter for non-text element issues
    alt_text_issues = [issue for issue in issues if issue.rule_id == 'IMG_MISSING_ALT']
    
    if alt_text_issues:
        return {
            'status': 'failed',
            'message': f'Found {len(alt_text_issues)} non-text elements without alternatives',
            'details': {
                'issues': [issue.__dict__ for issue in alt_text_issues],
                'section_508': '§1194.22(a)',
                'requirement': 'Text equivalent for non-text elements'
            }
        }
    
    return {
        'status': 'passed',
        'message': 'All non-text elements have equivalent alternatives',
        'details': {
            'section_508': '§1194.22(a)',
            'requirement': 'Text equivalent for non-text elements'
        }
    }


def test_color_independence(context: Dict[str, Any]) -> Dict[str, Any]:
    """Test §1194.22(c): Information not conveyed by color alone."""
    html_content = context.get('html_content', '')
    
    if not html_content:
        return {
            'status': 'skipped',
            'message': 'No HTML content provided for testing'
        }
    
    # Check for color-dependent information patterns
    color_dependent_patterns = [
        'required field',
        'error',
        'success',
        'warning',
        'click the red button',
        'green means go'
    ]
    
    found_patterns = []
    for pattern in color_dependent_patterns:
        if pattern in html_content.lower():
            found_patterns.append(pattern)
    
    if found_patterns:
        return {
            'status': 'warning',
            'message': f'Found {len(found_patterns)} potential color-dependent information patterns',
            'details': {
                'patterns': found_patterns,
                'section_508': '§1194.22(c)',
                'requirement': 'Information not conveyed by color alone',
                'note': 'Manual review recommended to verify color independence'
            }
        }
    
    return {
        'status': 'passed',
        'message': 'No obvious color-dependent information detected',
        'details': {
            'section_508': '§1194.22(c)',
            'requirement': 'Information not conveyed by color alone'
        }
    }


def test_document_structure(context: Dict[str, Any]) -> Dict[str, Any]:
    """Test §1194.22(d): Documents readable without style sheets."""
    html_content = context.get('html_content', '')
    
    if not html_content:
        return {
            'status': 'skipped',
            'message': 'No HTML content provided for testing'
        }
    
    from ...core.static_analyzer import StaticAnalyzer
    
    analyzer = StaticAnalyzer()
    issues = analyzer.analyze_html(html_content)
    
    # Check for proper document structure
    structure_issues = [issue for issue in issues 
                       if issue.rule_id in ['NO_HEADINGS', 'SKIPPED_HEADING_LEVEL']]
    
    if structure_issues:
        return {
            'status': 'failed',
            'message': f'Found {len(structure_issues)} document structure issues',
            'details': {
                'issues': [issue.__dict__ for issue in structure_issues],
                'section_508': '§1194.22(d)',
                'requirement': 'Documents readable without style sheets'
            }
        }
    
    return {
        'status': 'passed',
        'message': 'Document structure is accessible without style sheets',
        'details': {
            'section_508': '§1194.22(d)',
            'requirement': 'Documents readable without style sheets'
        }
    }


def test_image_maps(context: Dict[str, Any]) -> Dict[str, Any]:
    """Test §1194.22(e): Redundant text links for server-side image maps."""
    html_content = context.get('html_content', '')
    
    if not html_content:
        return {
            'status': 'skipped',
            'message': 'No HTML content provided for testing'
        }
    
    # Check for server-side image maps
    if 'ismap' in html_content.lower():
        # Look for redundant text links
        if 'href=' in html_content.lower():
            return {
                'status': 'passed',
                'message': 'Server-side image map with redundant text links found',
                'details': {
                    'section_508': '§1194.22(e)',
                    'requirement': 'Redundant text links for server-side image maps'
                }
            }
        else:
            return {
                'status': 'failed',
                'message': 'Server-side image map without redundant text links',
                'details': {
                    'section_508': '§1194.22(e)',
                    'requirement': 'Redundant text links for server-side image maps',
                    'suggestion': 'Add redundant text links for image map areas'
                }
            }
    
    return {
        'status': 'passed',
        'message': 'No server-side image maps detected',
        'details': {
            'section_508': '§1194.22(e)',
            'requirement': 'Redundant text links for server-side image maps'
        }
    }


def test_client_side_image_maps(context: Dict[str, Any]) -> Dict[str, Any]:
    """Test §1194.22(f): Client-side image maps with alt text."""
    html_content = context.get('html_content', '')
    
    if not html_content:
        return {
            'status': 'skipped',
            'message': 'No HTML content provided for testing'
        }
    
    # Check for client-side image maps
    if 'usemap=' in html_content.lower():
        # Check for alt text on map areas
        if 'alt=' in html_content.lower():
            return {
                'status': 'passed',
                'message': 'Client-side image map with alt text found',
                'details': {
                    'section_508': '§1194.22(f)',
                    'requirement': 'Client-side image maps with alt text'
                }
            }
        else:
            return {
                'status': 'failed',
                'message': 'Client-side image map without alt text',
                'details': {
                    'section_508': '§1194.22(f)',
                    'requirement': 'Client-side image maps with alt text',
                    'suggestion': 'Add alt text to map area elements'
                }
            }
    
    return {
        'status': 'passed',
        'message': 'No client-side image maps detected',
        'details': {
            'section_508': '§1194.22(f)',
            'requirement': 'Client-side image maps with alt text'
        }
    }


def test_data_table_headers(context: Dict[str, Any]) -> Dict[str, Any]:
    """Test §1194.22(g): Row and column headers for data tables."""
    html_content = context.get('html_content', '')
    
    if not html_content:
        return {
            'status': 'skipped',
            'message': 'No HTML content provided for testing'
        }
    
    # Check for data tables
    if '<table' in html_content.lower():
        # Check for header elements
        if '<th' in html_content.lower():
            return {
                'status': 'passed',
                'message': 'Data tables with header elements found',
                'details': {
                    'section_508': '§1194.22(g)',
                    'requirement': 'Row and column headers for data tables'
                }
            }
        else:
            return {
                'status': 'warning',
                'message': 'Tables found without obvious header elements',
                'details': {
                    'section_508': '§1194.22(g)',
                    'requirement': 'Row and column headers for data tables',
                    'note': 'Manual review recommended to verify table structure'
                }
            }
    
    return {
        'status': 'passed',
        'message': 'No data tables detected',
        'details': {
            'section_508': '§1194.22(g)',
            'requirement': 'Row and column headers for data tables'
        }
    }


def test_complex_table_headers(context: Dict[str, Any]) -> Dict[str, Any]:
    """Test §1194.22(h): Markup for complex table headers."""
    html_content = context.get('html_content', '')
    
    if not html_content:
        return {
            'status': 'skipped',
            'message': 'No HTML content provided for testing'
        }
    
    # Check for complex table structures
    if '<table' in html_content.lower() and ('colspan=' in html_content.lower() or 'rowspan=' in html_content.lower()):
        # Check for header markup
        if 'scope=' in html_content.lower() or 'headers=' in html_content.lower():
            return {
                'status': 'passed',
                'message': 'Complex tables with proper header markup found',
                'details': {
                    'section_508': '§1194.22(h)',
                    'requirement': 'Markup for complex table headers'
                }
            }
        else:
            return {
                'status': 'warning',
                'message': 'Complex tables detected without obvious header markup',
                'details': {
                    'section_508': '§1194.22(h)',
                    'requirement': 'Markup for complex table headers',
                    'note': 'Manual review recommended to verify header associations'
                }
            }
    
    return {
        'status': 'passed',
        'message': 'No complex tables detected',
        'details': {
            'section_508': '§1194.22(h)',
            'requirement': 'Markup for complex table headers'
        }
    }


def test_frames_with_titles(context: Dict[str, Any]) -> Dict[str, Any]:
    """Test §1194.22(i): Frames with titles."""
    html_content = context.get('html_content', '')
    
    if not html_content:
        return {
            'status': 'skipped',
            'message': 'No HTML content provided for testing'
        }
    
    # Check for frames
    if '<frame' in html_content.lower():
        # Check for title attributes
        if 'title=' in html_content.lower():
            return {
                'status': 'passed',
                'message': 'Frames with title attributes found',
                'details': {
                    'section_508': '§1194.22(i)',
                    'requirement': 'Frames with titles'
                }
            }
        else:
            return {
                'status': 'failed',
                'message': 'Frames without title attributes',
                'details': {
                    'section_508': '§1194.22(i)',
                    'requirement': 'Frames with titles',
                    'suggestion': 'Add title attributes to frame elements'
                }
            }
    
    return {
        'status': 'passed',
        'message': 'No frames detected',
        'details': {
            'section_508': '§1194.22(i)',
            'requirement': 'Frames with titles'
        }
    }


def test_flicker_avoidance(context: Dict[str, Any]) -> Dict[str, Any]:
    """Test §1194.22(j): Avoid screen flicker."""
    html_content = context.get('html_content', '')
    
    if not html_content:
        return {
            'status': 'skipped',
            'message': 'No HTML content provided for testing'
        }
    
    # Check for potential flicker-inducing content
    flicker_patterns = [
        'blink',
        'marquee',
        'animation',
        'transition',
        'flash'
    ]
    
    found_patterns = []
    for pattern in flicker_patterns:
        if pattern in html_content.lower():
            found_patterns.append(pattern)
    
    if found_patterns:
        return {
            'status': 'warning',
            'message': f'Found {len(found_patterns)} potential flicker-inducing elements',
            'details': {
                'patterns': found_patterns,
                'section_508': '§1194.22(j)',
                'requirement': 'Avoid screen flicker',
                'note': 'Manual review recommended to verify flicker rates'
            }
        }
    
    return {
        'status': 'passed',
        'message': 'No obvious flicker-inducing content detected',
        'details': {
            'section_508': '§1194.22(j)',
            'requirement': 'Avoid screen flicker'
        }
    }


def test_text_only_alternative(context: Dict[str, Any]) -> Dict[str, Any]:
    """Test §1194.22(k): Text-only page alternative."""
    # This test requires checking for alternative pages
    # For now, we'll check for common patterns
    
    html_content = context.get('html_content', '')
    
    if not html_content:
        return {
            'status': 'skipped',
            'message': 'No HTML content provided for testing'
        }
    
    # Check for text-only indicators
    text_only_patterns = [
        'text only',
        'text-only',
        'accessible version',
        'screen reader version'
    ]
    
    found_patterns = []
    for pattern in text_only_patterns:
        if pattern in html_content.lower():
            found_patterns.append(pattern)
    
    if found_patterns:
        return {
            'status': 'passed',
            'message': 'Text-only alternative indicators found',
            'details': {
                'patterns': found_patterns,
                'section_508': '§1194.22(k)',
                'requirement': 'Text-only page alternative'
            }
        }
    
    return {
        'status': 'info',
        'message': 'No text-only alternative indicators detected',
        'details': {
            'section_508': '§1194.22(k)',
            'requirement': 'Text-only page alternative',
            'note': 'Consider providing a text-only alternative for complex pages'
        }
    }


def test_script_alternatives(context: Dict[str, Any]) -> Dict[str, Any]:
    """Test §1194.22(l): Script alternatives."""
    html_content = context.get('html_content', '')
    
    if not html_content:
        return {
            'status': 'skipped',
            'message': 'No HTML content provided for testing'
        }
    
    # Check for scripts
    if '<script' in html_content.lower():
        # Check for noscript elements
        if '<noscript' in html_content.lower():
            return {
                'status': 'passed',
                'message': 'Scripts with noscript alternatives found',
                'details': {
                    'section_508': '§1194.22(l)',
                    'requirement': 'Script alternatives'
                }
            }
        else:
            return {
                'status': 'warning',
                'message': 'Scripts detected without obvious alternatives',
                'details': {
                    'section_508': '§1194.22(l)',
                    'requirement': 'Script alternatives',
                    'note': 'Consider adding noscript elements or server-side alternatives'
                }
            }
    
    return {
        'status': 'passed',
        'message': 'No scripts detected',
        'details': {
            'section_508': '§1194.22(l)',
            'requirement': 'Script alternatives'
        }
    }


def test_applet_alternatives(context: Dict[str, Any]) -> Dict[str, Any]:
    """Test §1194.22(m): Applet alternatives."""
    html_content = context.get('html_content', '')
    
    if not html_content:
        return {
            'status': 'skipped',
            'message': 'No HTML content provided for testing'
        }
    
    # Check for applets (largely obsolete, but still covered)
    if '<applet' in html_content.lower():
        # Check for alt text or alternative content
        if 'alt=' in html_content.lower():
            return {
                'status': 'passed',
                'message': 'Applets with alt text found',
                'details': {
                    'section_508': '§1194.22(m)',
                    'requirement': 'Applet alternatives'
                }
            }
        else:
            return {
                'status': 'failed',
                'message': 'Applets without alt text',
                'details': {
                    'section_508': '§1194.22(m)',
                    'requirement': 'Applet alternatives',
                    'suggestion': 'Add alt text to applet elements'
                }
            }
    
    return {
        'status': 'passed',
        'message': 'No applets detected',
        'details': {
            'section_508': '§1194.22(m)',
            'requirement': 'Applet alternatives'
        }
    }


def test_electronic_forms(context: Dict[str, Any]) -> Dict[str, Any]:
    """Test §1194.22(n): Electronic forms accessibility."""
    html_content = context.get('html_content', '')
    
    if not html_content:
        return {
            'status': 'skipped',
            'message': 'No HTML content provided for testing'
        }
    
    from ...core.static_analyzer import StaticAnalyzer
    
    analyzer = StaticAnalyzer()
    issues = analyzer.analyze_html(html_content)
    
    # Check for form accessibility issues
    form_issues = [issue for issue in issues if issue.rule_id == 'FORM_CONTROL_NO_LABEL']
    
    if form_issues:
        return {
            'status': 'failed',
            'message': f'Found {len(form_issues)} form accessibility issues',
            'details': {
                'issues': [issue.__dict__ for issue in form_issues],
                'section_508': '§1194.22(n)',
                'requirement': 'Electronic forms accessibility'
            }
        }
    
    return {
        'status': 'passed',
        'message': 'Forms appear to be accessible',
        'details': {
            'section_508': '§1194.22(n)',
            'requirement': 'Electronic forms accessibility'
        }
    }


def test_navigation_links(context: Dict[str, Any]) -> Dict[str, Any]:
    """Test §1194.22(o): Navigation links."""
    html_content = context.get('html_content', '')
    
    if not html_content:
        return {
            'status': 'skipped',
            'message': 'No HTML content provided for testing'
        }
    
    # Check for navigation elements
    if '<nav' in html_content.lower() or 'navigation' in html_content.lower():
        return {
            'status': 'passed',
            'message': 'Navigation elements found',
            'details': {
                'section_508': '§1194.22(o)',
                'requirement': 'Navigation links'
            }
        }
    
    return {
        'status': 'info',
        'message': 'No explicit navigation elements detected',
        'details': {
            'section_508': '§1194.22(o)',
            'requirement': 'Navigation links',
            'note': 'Consider adding semantic navigation elements'
        }
    }


def test_skip_navigation(context: Dict[str, Any]) -> Dict[str, Any]:
    """Test §1194.22(p): Skip navigation links."""
    html_content = context.get('html_content', '')
    
    if not html_content:
        return {
            'status': 'skipped',
            'message': 'No HTML content provided for testing'
        }
    
    # Check for skip navigation patterns
    skip_patterns = ['skip', 'jump to', 'go to main', 'skip navigation']
    has_skip_links = any(pattern in html_content.lower() for pattern in skip_patterns)
    
    if has_skip_links:
        return {
            'status': 'passed',
            'message': 'Skip navigation links found',
            'details': {
                'section_508': '§1194.22(p)',
                'requirement': 'Skip navigation links'
            }
        }
    
    return {
        'status': 'failed',
        'message': 'No skip navigation links detected',
        'details': {
            'section_508': '§1194.22(p)',
            'requirement': 'Skip navigation links',
            'suggestion': 'Add skip navigation links for keyboard users'
        }
    }


# Create test case objects
SECTION_508_TEST_CASES = [
    TestCase(
        name="Equivalent Alternatives",
        description="§1194.22(a): Text equivalent for non-text elements",
        test_function=test_equivalent_alternatives,
        category="Section 508",
        priority="critical"
    ),
    TestCase(
        name="Color Independence",
        description="§1194.22(c): Information not conveyed by color alone",
        test_function=test_color_independence,
        category="Section 508",
        priority="high"
    ),
    TestCase(
        name="Document Structure",
        description="§1194.22(d): Documents readable without style sheets",
        test_function=test_document_structure,
        category="Section 508",
        priority="high"
    ),
    TestCase(
        name="Image Maps",
        description="§1194.22(e): Redundant text links for server-side image maps",
        test_function=test_image_maps,
        category="Section 508",
        priority="medium"
    ),
    TestCase(
        name="Client-Side Image Maps",
        description="§1194.22(f): Client-side image maps with alt text",
        test_function=test_client_side_image_maps,
        category="Section 508",
        priority="medium"
    ),
    TestCase(
        name="Data Table Headers",
        description="§1194.22(g): Row and column headers for data tables",
        test_function=test_data_table_headers,
        category="Section 508",
        priority="high"
    ),
    TestCase(
        name="Complex Table Headers",
        description="§1194.22(h): Markup for complex table headers",
        test_function=test_complex_table_headers,
        category="Section 508",
        priority="medium"
    ),
    TestCase(
        name="Frames with Titles",
        description="§1194.22(i): Frames with titles",
        test_function=test_frames_with_titles,
        category="Section 508",
        priority="medium"
    ),
    TestCase(
        name="Flicker Avoidance",
        description="§1194.22(j): Avoid screen flicker",
        test_function=test_flicker_avoidance,
        category="Section 508",
        priority="high"
    ),
    TestCase(
        name="Text-Only Alternative",
        description="§1194.22(k): Text-only page alternative",
        test_function=test_text_only_alternative,
        category="Section 508",
        priority="medium"
    ),
    TestCase(
        name="Script Alternatives",
        description="§1194.22(l): Script alternatives",
        test_function=test_script_alternatives,
        category="Section 508",
        priority="high"
    ),
    TestCase(
        name="Applet Alternatives",
        description="§1194.22(m): Applet alternatives",
        test_function=test_applet_alternatives,
        category="Section 508",
        priority="low"
    ),
    TestCase(
        name="Electronic Forms",
        description="§1194.22(n): Electronic forms accessibility",
        test_function=test_electronic_forms,
        category="Section 508",
        priority="critical"
    ),
    TestCase(
        name="Navigation Links",
        description="§1194.22(o): Navigation links",
        test_function=test_navigation_links,
        category="Section 508",
        priority="medium"
    ),
    TestCase(
        name="Skip Navigation",
        description="§1194.22(p): Skip navigation links",
        test_function=test_skip_navigation,
        category="Section 508",
        priority="high"
    )
] 