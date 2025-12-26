# Network Diagnostics Tool

A web-based network diagnostic tool that provides a terminal-style interface for running common network diagnostic commands like NSLookup, Ping, Dig, Traceroute, and port testing. Features both a web UI and REST API.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)

## Features

- **🔍 NSLookup**: Perform DNS lookups with custom DNS servers
- **📡 Ping**: Test network connectivity and latency
- **🔎 Dig**: Query specific DNS record types (A, MX, NS, TXT, CNAME, SOA, PTR, AAAA)
- **🗺️ TraceRoute**: Trace the network path to a destination
- **🔌 Port Testing**: Check if TCP/UDP ports are open
- **📊 Bulk Processing**: Upload CSV files for batch DNS lookups
- **🎨 Dual Themes**: Retro terminal and modern professional themes
- **🔧 REST API**: Programmatic access to all diagnostic tools
- **📝 Auto-logging**: API usage tracking and monitoring

## Screenshots

*Web Interface with both Modern and Retro themes*

## Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/techbutton/network-diagnostics-tool.git
   cd network-diagnostics-tool
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the application**:
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Access the web interface**:
   Open your browser and navigate to `http://localhost:8080`

## Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and customize:

```bash
# Application Settings
APP_PORT=8080                           # Port to run the application on
CANONICAL_HOST=localhost:8080           # Canonical hostname for the app
ENABLE_CANONICAL_REDIRECT=false         # Force redirect to canonical host

# DNS Configuration
STATUS_CHECK_HOST=8.8.8.8               # DNS server to monitor for status
STATUS_CHECK_INTERVAL=300               # Status check interval (seconds)
CUSTOM_DNS_SERVERS=8.8.8.8,1.1.1.1,8.8.4.4,1.0.0.1  # Comma-separated DNS servers

# Optional: Auto-append domain for single-label hostnames
DEFAULT_DOMAIN=                         # e.g., example.com (leave empty to disable)

# Flask Environment
FLASK_ENV=production                    # production or development
```

### DNS Server Configuration

You can customize the DNS servers used by the tool:

```bash
# Example: Use Google and Cloudflare DNS
CUSTOM_DNS_SERVERS=8.8.8.8,1.1.1.1,8.8.4.4,1.0.0.1

# Example: Use your corporate DNS servers
CUSTOM_DNS_SERVERS=10.0.0.1,10.0.0.2,10.0.0.3
```

### Default Domain (Optional)

If you frequently query hostnames in a specific domain, you can set a default domain:

```bash
# Automatically append .example.com to single-label hostnames
DEFAULT_DOMAIN=example.com
```

With this setting, querying "server01" will automatically become "server01.example.com".

## Usage

### Web Interface

1. **Select a diagnostic tool** from the dropdown menu
2. **Enter the target hostname or IP address**
3. **Configure tool-specific options** (DNS server, record type, port, etc.)
4. **Click "Run Diagnostic"** to execute
5. **View results** in the terminal-style output box

### Bulk NSLookup

1. Select "Bulk NSLookup" from the tool dropdown
2. Upload a CSV file containing hostnames (one per line or comma-separated)
3. Optionally enable ping and reverse DNS lookup
4. Click "Upload & Process"
5. Download the results as a CSV file

### Theme Toggle

Click the theme toggle button in the header to switch between:
- **Retro Theme**: Classic terminal look with green text on black
- **Modern Theme**: Professional interface with clean design

## API Documentation

All diagnostic tools are accessible via REST API. The API supports both GET and POST requests.

### API Endpoints

#### NSLookup
```bash
# GET request
curl "http://localhost:8080/api/nslookup?target=google.com&dns_server=8.8.8.8"

# POST request
curl -X POST http://localhost:8080/api/nslookup \
  -H "Content-Type: application/json" \
  -d '{"target": "google.com", "dns_server": "8.8.8.8"}'
```

#### Ping
```bash
# GET request
curl "http://localhost:8080/api/ping?target=google.com&count=4"

# POST request
curl -X POST http://localhost:8080/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "google.com", "count": 4}'
```

#### Dig
```bash
# GET request
curl "http://localhost:8080/api/dig?target=google.com&type=MX&dns_server=8.8.8.8"

# POST request
curl -X POST http://localhost:8080/api/dig \
  -H "Content-Type: application/json" \
  -d '{"target": "google.com", "type": "MX", "dns_server": "8.8.8.8"}'
```

#### Traceroute
```bash
# GET request
curl "http://localhost:8080/api/traceroute?target=google.com"

# POST request
curl -X POST http://localhost:8080/api/traceroute \
  -H "Content-Type: application/json" \
  -d '{"target": "google.com"}'
```

#### Port Test
```bash
# GET request
curl "http://localhost:8080/api/netconnection?target=google.com&port=443&protocol=tcp"

# POST request
curl -X POST http://localhost:8080/api/netconnection \
  -H "Content-Type: application/json" \
  -d '{"target": "google.com", "port": 443, "protocol": "tcp"}'
```

### API Response Format

```json
{
  "success": true,
  "target": "google.com",
  "dns_server": "8.8.8.8",
  "result": "Name: google.com\nAddress: 142.250.185.46",
  "timestamp": "2024-12-26T10:30:00Z"
}
```

For complete API documentation, visit `/api/docs` after starting the application.

## Development Mode

Enable development mode for debugging and testing:

```bash
# In .env file
FLASK_ENV=development
```

Development mode features:
- Flask development server (auto-reload on code changes)
- Orange warning banner at the top of the page
- Detailed error messages
- Debug logging

## Production Deployment

### Using Waitress (Recommended)

The application automatically uses Waitress in production mode:

```bash
# In .env file
FLASK_ENV=production
```

Waitress is a production-quality pure-Python WSGI server that provides:
- Better performance than Flask's built-in server
- Multi-threading support (25 threads by default)
- Proper handling of concurrent requests

### Using Gunicorn (Linux/Mac)

If you prefer Gunicorn, you can run:

```bash
gunicorn -c gunicorn_config.py app:app
```

### Using a Reverse Proxy (Nginx/Apache)

For production deployments, it's recommended to use a reverse proxy:

**Nginx example configuration**:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Running as a System Service

Create a systemd service file on Linux:

```bash
sudo nano /etc/systemd/system/netdiag.service
```

```ini
[Unit]
Description=Network Diagnostics Tool
After=network.target

[Service]
User=your-user
WorkingDirectory=/path/to/network-diagnostics-tool
Environment="PATH=/path/to/network-diagnostics-tool/venv/bin"
ExecStart=/path/to/network-diagnostics-tool/venv/bin/python app.py

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable netdiag
sudo systemctl start netdiag
sudo systemctl status netdiag
```

## Project Structure

```
network-diagnostics-tool/
├── app.py                  # Main application file
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment configuration
├── README.md              # This file
├── templates/             # HTML templates
│   ├── index.html        # Main interface
│   └── api_docs.html     # API documentation
├── logs/                  # Application logs (auto-created)
└── bulk_results/          # Temporary bulk processing results (auto-created)
```

## Security Considerations

- **Input Validation**: All user inputs are validated to prevent command injection
- **DNS Security**: Be cautious when using untrusted DNS servers
- **Firewall Rules**: Consider restricting access to the application
- **HTTPS**: Use a reverse proxy with SSL/TLS for production
- **Rate Limiting**: Consider adding rate limiting for the API endpoints
- **Logging**: Review logs regularly for suspicious activity

## Troubleshooting

### Common Issues

**Port already in use**:
```bash
# Change the port in .env
APP_PORT=8081
```

**DNS lookup fails**:
- Verify DNS server is reachable
- Check firewall rules
- Try a different DNS server (8.8.8.8, 1.1.1.1)

**Traceroute not working**:
- Linux: Install traceroute: `sudo apt-get install traceroute`
- Windows: Built-in as `tracert`

**Dig command not found**:
- Linux: `sudo apt-get install dnsutils`
- Mac: `brew install bind`
- Windows: Use WSL or install BIND tools

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

### Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Update documentation for new features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Uses [dnspython](https://www.dnspython.org/) for DNS operations
- Styled with custom CSS for retro terminal aesthetics
- Deployed with [Waitress](https://docs.pylonsproject.org/projects/waitress/)

## Support

For bug reports and feature requests, please use the [GitHub Issues](https://github.com/techbutton/network-diagnostics-tool/issues) page.

## Changelog

### Version 1.0.0 (2024-12-26)
- Initial open-source release
- Web interface with dual themes
- REST API for all diagnostic tools
- Bulk NSLookup processing
- Customizable DNS servers
- Auto-domain appending for single-label hostnames
- Production-ready with Waitress server

## Roadmap

- [ ] Add support for IPv6 diagnostics
- [ ] Implement rate limiting for API
- [ ] Add user authentication
- [ ] Export results in multiple formats (JSON, XML)
- [ ] Add scheduling for recurring diagnostics
- [ ] Dashboard for historical results
- [ ] Docker containerization
- [ ] Kubernetes deployment guide

---

**Made by [techbutton](https://github.com/techbutton)** | **Star ⭐ this repo if you find it useful!**
