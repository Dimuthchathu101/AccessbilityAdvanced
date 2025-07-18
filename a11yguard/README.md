# a11yguard - Advanced Accessibility Testing Tool

A comprehensive accessibility testing tool that combines automated testing, static analysis, and reporting to ensure web content meets accessibility standards including WCAG 2.2 and Section 508.

## 🚀 Features

- **Automated Testing**: Integration with axe-core for comprehensive accessibility testing
- **Static Analysis**: HTML/ARIA validation without requiring a browser
- **Multiple Standards**: Support for WCAG 2.2, Section 508, and custom rulesets
- **Comprehensive Reporting**: Generate reports in JSON, HTML, CSV, and Markdown formats
- **CI/CD Integration**: Built-in support for GitHub Actions, GitLab CI, Jenkins, and more
- **Screen Reader Testing**: Utilities for testing screen reader compatibility
- **Tenon.io Integration**: Optional integration with Tenon.io API for additional testing
- **Docker Support**: Containerized deployment for consistent environments

## 📋 Requirements

- Python 3.8+
- Chrome/Chromium browser
- ChromeDriver (automatically managed)

## 🛠️ Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/your-org/a11yguard.git
cd a11yguard

# Install dependencies
pip install -r requirements.txt

# Make the CLI executable
chmod +x main.py
```

### Using Docker

```bash
# Build the Docker image
docker build -t a11yguard .

# Run tests
docker run -v $(pwd)/outputs:/app/outputs a11yguard test https://example.com
```

## 🚀 Quick Start

### Basic Usage

```bash
# Test a single URL
python main.py test https://example.com

# Test multiple URLs
python main.py test https://example.com https://example.org

# Test URLs from a file
python main.py test --urls-file urls.txt

# Generate different report formats
python main.py test https://example.com --format json
python main.py test https://example.com --format csv
python main.py test https://example.com --format markdown
```

### Static Analysis

```bash
# Analyze an HTML file
python main.py analyze index.html

# Analyze with custom output format
python main.py analyze index.html --format json
```

### Test Suites

```bash
# Run WCAG 2.2 test suite
python main.py suite https://example.com --test-suite wcag

# Run Section 508 test suite
python main.py suite https://example.com --test-suite section508

# Run all test suites
python main.py suite https://example.com --test-suite all
```

### CI/CD Integration

```bash
# Run in CI environment
python main.py ci --urls-file urls.txt --max-violations 5
```

### Tenon.io Integration

```bash
# Set your API key
export TENON_API_KEY="your-api-key"

# Run tests with Tenon.io
python main.py tenon --urls-file urls.txt
```

## 📁 Project Structure

```
a11yguard/
├── core/                    # Core functionality
│   ├── axe_runner.py       # Axe-core integration
│   ├── static_analyzer.py  # HTML/ARIA validation
│   ├── reporter.py         # Report generation
│   └── screen_reader.py    # Screen reader helpers
├── integrations/           # External integrations
│   ├── tenon_client.py     # Tenon.io API
│   └── ci_cd.py           # CI/CD helpers
├── tests/                  # Test framework
│   ├── test_suite.py      # Test orchestrator
│   └── test_cases/        # Test case definitions
│       ├── wcag_2_2.py    # WCAG test cases
│       └── section_508.py # Section 508 cases
├── config/                 # Configuration files
│   ├── urls.yaml          # Test URLs
│   └── rulesets.yaml      # Custom rules
├── outputs/               # Generated outputs
│   ├── reports/           # Test reports
│   └── screenshots/       # Visual diffs
├── docker/                # Containerization
│   └── Dockerfile         # Docker configuration
├── requirements.txt       # Python dependencies
├── main.py               # CLI entrypoint
└── README.md             # This file
```

## ⚙️ Configuration

### URLs Configuration (`config/urls.yaml`)

```yaml
production:
  - name: "Homepage"
    url: "https://example.com"
    description: "Main homepage"
    priority: "critical"

staging:
  - name: "Staging Homepage"
    url: "https://staging.example.com"
    description: "Staging environment"
    priority: "high"
```

### Rulesets Configuration (`config/rulesets.yaml`)

```yaml
wcag_2_2_level_aa:
  name: "WCAG 2.2 Level AA"
  description: "Web Content Accessibility Guidelines 2.2 Level AA"
  rules:
    - "color-contrast"
    - "image-alt"
    - "label"
    - "link-name"
  priority: "high"
```

## 🔧 Advanced Usage

### Custom Rules

```python
# Define custom test cases
from tests.test_suite import TestCase

def custom_test_function(context):
    # Your custom test logic here
    return {'status': 'passed', 'message': 'Custom test passed'}

custom_test = TestCase(
    name="Custom Test",
    description="A custom accessibility test",
    test_function=custom_test_function,
    category="Custom",
    priority="high"
)
```

### CI/CD Integration

#### GitHub Actions

```yaml
name: Accessibility Tests
on: [push, pull_request]

jobs:
  accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run accessibility tests
        run: python main.py ci --urls-file urls.txt --max-violations 0
      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: accessibility-reports
          path: outputs/reports/
```

#### GitLab CI

```yaml
accessibility:
  stage: test
  image: python:3.11
  before_script:
    - pip install -r requirements.txt
  script:
    - python main.py ci --urls-file urls.txt --max-violations 0
  artifacts:
    paths:
      - outputs/reports/
    expire_in: 1 week
```

### Docker Compose

```yaml
version: '3.8'
services:
  a11yguard:
    build: .
    volumes:
      - ./outputs:/app/outputs
      - ./config:/app/config
    environment:
      - TENON_API_KEY=${TENON_API_KEY}
    command: ["test", "https://example.com"]
```

## 📊 Report Formats

### HTML Report
Comprehensive HTML reports with interactive elements, severity filtering, and detailed issue descriptions.

### JSON Report
Machine-readable JSON format for integration with other tools and APIs.

### CSV Report
Spreadsheet-friendly format for data analysis and tracking.

### Markdown Report
GitHub-friendly format for documentation and issue tracking.

## 🧪 Testing Standards

### WCAG 2.2
- **Level A**: Basic accessibility requirements
- **Level AA**: Enhanced accessibility (recommended)
- **Level AAA**: Maximum accessibility (optional)

### Section 508
- Federal accessibility requirements
- Required for government websites
- Based on WCAG 2.0 Level AA

### Custom Standards
- Organization-specific requirements
- Industry-specific guidelines
- Compliance frameworks

## 🔍 Available Tests

### Core Accessibility Tests
- **Alt Text**: Images have appropriate alternative text
- **Color Contrast**: Sufficient color contrast ratios
- **Form Labels**: Form controls have proper labels
- **Heading Structure**: Logical heading hierarchy
- **Keyboard Navigation**: All functionality accessible via keyboard
- **Landmark Elements**: Semantic page structure
- **Link Names**: Descriptive link text
- **Skip Links**: Navigation bypass options

### Advanced Tests
- **ARIA Attributes**: Proper ARIA implementation
- **Focus Management**: Logical focus order
- **Screen Reader**: Screen reader compatibility
- **Mobile Accessibility**: Touch target sizes and viewport settings
- **Dynamic Content**: Live regions and updates

## 🐛 Troubleshooting

### Common Issues

#### Chrome/ChromeDriver Issues
```bash
# Update ChromeDriver
pip install --upgrade webdriver-manager

# Use system Chrome
export CHROME_BIN=/usr/bin/google-chrome
```

#### Permission Issues
```bash
# Fix file permissions
chmod +x main.py
chmod -R 755 outputs/
```

#### Network Issues
```bash
# Use proxy settings
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

### Debug Mode
```bash
# Enable verbose logging
python main.py --verbose test https://example.com
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linting
flake8
black .

# Run type checking
mypy .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [axe-core](https://github.com/dequelabs/axe-core) - Accessibility testing engine
- [Tenon.io](https://tenon.io/) - Accessibility testing API
- [WCAG](https://www.w3.org/WAI/WCAG21/quickref/) - Web Content Accessibility Guidelines
- [Section 508](https://www.section508.gov/) - Federal accessibility requirements

## 📞 Support

- **Documentation**: [docs.example.com/a11yguard](https://docs.example.com/a11yguard)
- **Issues**: [GitHub Issues](https://github.com/your-org/a11yguard/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/a11yguard/discussions)
- **Email**: support@example.com

## 🔄 Changelog

### v1.0.0 (2024-01-01)
- Initial release
- Core accessibility testing functionality
- WCAG 2.2 and Section 508 support
- Multiple report formats
- CI/CD integration
- Docker support

---

**Made with ❤️ for a more accessible web** 