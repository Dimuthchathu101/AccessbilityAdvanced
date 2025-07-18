"""
a11yguard - Advanced Accessibility Testing Tool

A comprehensive accessibility testing tool that combines automated testing,
static analysis, and reporting to ensure web content meets accessibility standards.
"""

__version__ = "1.0.0"
__author__ = "a11yguard Team"
__email__ = "support@example.com"

from .core.axe_runner import AxeRunner
from .core.static_analyzer import StaticAnalyzer
from .core.reporter import ReportGenerator
from .core.screen_reader import ScreenReaderHelper
from .integrations.tenon_client import TenonClient
from .integrations.ci_cd import CICDHelper
from .tests.test_suite import TestSuite

__all__ = [
    'AxeRunner',
    'StaticAnalyzer', 
    'ReportGenerator',
    'ScreenReaderHelper',
    'TenonClient',
    'CICDHelper',
    'TestSuite'
] 