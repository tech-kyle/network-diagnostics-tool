# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-26

### Added
- Initial open-source release
- Web interface with terminal-style output
- Dual theme support (Retro and Modern)
- NSLookup diagnostic tool with custom DNS server selection
- Ping diagnostic tool with configurable packet count
- Dig tool for DNS record queries (A, MX, NS, TXT, CNAME, SOA, PTR, AAAA)
- TraceRoute functionality
- TCP/UDP port testing
- Bulk NSLookup processing from CSV files
- REST API for all diagnostic tools
- API documentation page
- Automatic domain appending for single-label hostnames (configurable)
- DNS server status monitoring
- API usage logging with rotation
- Development mode with visual indicator
- Environment-based configuration via .env files
- Production-ready Waitress WSGI server
- Comprehensive README with setup instructions
- Setup scripts for Windows (PowerShell) and Linux/Mac (Bash)
- MIT License
- Contributing guidelines
- .gitignore for Python projects

### Security
- Input validation on all user inputs
- Command injection prevention
- Safe subprocess execution

## [Unreleased]

### Planned Features
- User authentication and authorization
- IPv6 diagnostics enhancement
- Rate limiting for API endpoints
- Historical results dashboard
- Multiple export formats (JSON, XML, CSV)
- Scheduled/recurring diagnostics
- Docker containerization
- Kubernetes deployment configurations
- WebSocket support for real-time updates
- Multi-language support
- Dark/Light theme auto-detection

---

For detailed information about each release, see the [GitHub Releases](https://github.com/techbutton/network-diagnostics-tool/releases) page.
