# Contributing to Network Diagnostics Tool

Thank you for considering contributing to Network Diagnostics Tool! This document outlines the process for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/network-diagnostics-tool.git
   cd network-diagnostics-tool
   ```
3. **Set up the development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Development Workflow

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and test thoroughly

3. **Commit your changes** with clear, descriptive commit messages:
   ```bash
   git add .
   git commit -m "Add feature: description of your feature"
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Submit a Pull Request** on GitHub

## Code Style Guidelines

### Python
- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise
- Maximum line length: 120 characters

### HTML/CSS
- Use consistent indentation (2 spaces)
- Keep CSS organized and commented
- Use semantic HTML5 elements
- Ensure responsive design principles

### JavaScript
- Use modern ES6+ syntax
- Keep functions pure when possible
- Add comments for complex logic
- Use meaningful variable names

## Testing

Before submitting a PR:

1. **Test all diagnostic tools**:
   - NSLookup with various hostnames and IPs
   - Ping with different targets
   - Dig with various record types
   - Traceroute functionality
   - Port testing (TCP/UDP)
   - Bulk NSLookup with CSV files

2. **Test both themes**:
   - Retro theme
   - Modern theme

3. **Test API endpoints**:
   - All GET and POST methods
   - Error handling
   - Response formats

4. **Test in different environments**:
   - Development mode
   - Production mode
   - Different browsers (if UI changes)

## Pull Request Process

1. **Update documentation** if you're changing functionality
2. **Ensure all tests pass** before submitting
3. **Provide a clear PR description** explaining:
   - What changes you made
   - Why you made them
   - Any breaking changes
   - Screenshots (if UI changes)

4. **Link related issues** in your PR description
5. **Be responsive** to review comments and feedback

## Bug Reports

When filing a bug report, please include:

1. **Description** of the bug
2. **Steps to reproduce**
3. **Expected behavior**
4. **Actual behavior**
5. **Environment details**:
   - OS and version
   - Python version
   - Browser (if web UI issue)
6. **Screenshots** or error messages (if applicable)

Use the GitHub Issues page to report bugs.

## Feature Requests

We welcome feature requests! Please:

1. **Check existing issues** first to avoid duplicates
2. **Clearly describe the feature** and its benefits
3. **Provide use cases** to help understand the need
4. **Be open to discussion** about implementation

## Code of Conduct

### Our Standards

- **Be respectful** and inclusive
- **Be collaborative** and constructive
- **Focus on what's best** for the community
- **Show empathy** towards other community members

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information
- Other conduct inappropriate in a professional setting

## Questions?

Feel free to:
- Open an issue for questions about contributing
- Reach out via GitHub Discussions
- Contact the maintainers

## License

By contributing to Network Diagnostics Tool, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make Network Diagnostics Tool better!
