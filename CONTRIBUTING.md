# Contributing to Shadow AI Detection

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Check if the issue already exists
2. Create a new issue with:
   - Clear description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)

### Adding New Framework Signatures

One of the most valuable contributions is adding support for new AI frameworks:

1. **Create a test script**:
   ```bash
   cp tests/TEMPLATE_python.py tests/[framework]_test.py
   ```

2. **Implement the test**:
   - Import the framework
   - Create a client with a fake API key
   - Make an API call (will fail auth, but completes TLS handshake)

3. **Capture and extract**:
   ```bash
   python tests/[framework]_test.py
   python scripts/ja4_calculator.py pcaps/[framework]_*.pcap
   ```

4. **Update the database**:
   - Add entry to `signatures/signature_database.csv`
   - Include framework name, version, JA4 signature, and verification details

5. **Submit a pull request** with:
   - Test script
   - Updated signature database
   - Documentation of verification runs (3x consistency check)

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**:
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation as needed
4. **Test your changes**: Run relevant tests
5. **Commit with clear messages**: `git commit -m "Add: description of change"`
6. **Push and create pull request**

### Code Style

- Follow PEP 8 for Python code
- Use descriptive variable names
- Add docstrings to functions and classes
- Keep functions focused and small

### Testing Requirements

- New framework tests must run successfully
- Signature extraction must be verified (3x consistency)
- Database updates must include all required fields

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/shadow-ai-detection.git
cd shadow-ai-detection

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_all_frameworks.py
python validate_signatures.py
```

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add yourself to CONTRIBUTORS.md (if applicable)
4. Create pull request with clear description
5. Respond to review feedback

## Questions?

Open an issue with the `question` label, or check existing issues for answers.

Thank you for contributing! 🎉

