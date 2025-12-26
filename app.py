# Import necessary libraries
from flask import Flask, render_template, request, session, jsonify, Response, redirect
import subprocess
import platform
import os
import sys
import logging
import logging.handlers
import re
import random
import socket
import shutil
import uuid
import datetime
import json
import ipaddress
import dns.resolver
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = os.urandom(24)
logging.basicConfig(level=logging.INFO)

# ============================================================================
# ENVIRONMENT VARIABLE CONFIGURATION
# ============================================================================

# Application Configuration
APP_PORT = int(os.getenv('APP_PORT', '8080'))
CANONICAL_HOST = os.getenv('CANONICAL_HOST', 'localhost:8080')
ENABLE_CANONICAL_REDIRECT = os.getenv('ENABLE_CANONICAL_REDIRECT', 'false').lower() in ('true', '1', 'yes')

# DNS Status Monitoring
STATUS_CHECK_HOST = os.getenv('STATUS_CHECK_HOST', '8.8.8.8')
STATUS_CHECK_INTERVAL = int(os.getenv('STATUS_CHECK_INTERVAL', '300'))  # Default: 5 minutes

# Custom DNS Servers (comma-separated)
CUSTOM_DNS_SERVERS_STR = os.getenv('CUSTOM_DNS_SERVERS', '8.8.8.8,1.1.1.1,8.8.4.4,1.0.0.1')
CUSTOM_DNS_SERVERS_FROM_ENV = [s.strip() for s in CUSTOM_DNS_SERVERS_STR.split(',') if s.strip()]

# Default domain for single-label hostnames
DEFAULT_DOMAIN = os.getenv('DEFAULT_DOMAIN', '')

# Flask Environment
FLASK_ENV = os.getenv('FLASK_ENV', 'production')

# ============================================================================

# Define base directories for storing results and logs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BULK_RESULTS_DIR = os.path.join(BASE_DIR, 'bulk_results')
os.makedirs(BULK_RESULTS_DIR, exist_ok=True)
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

@app.before_request
def enforce_canonical_host_and_log():
    """Before each request, enforce a canonical hostname and log API-like usage."""
    try:
        host = request.host or ''
        path = request.path or ''
        remote = request.remote_addr or request.environ.get('REMOTE_ADDR')
        ua = request.headers.get('User-Agent', '')

        if ENABLE_CANONICAL_REDIRECT and request.method == 'GET' and path == '/' and host.lower() != CANONICAL_HOST.lower():
            protocol = 'https' if request.is_secure else 'http'
            canonical = f"{protocol}://{CANONICAL_HOST}{request.full_path if request.query_string else '/'}"
            return ('', 302, {'Location': canonical})
        
        looks_like_api = False
        if request.headers.get('Authorization'):
            looks_like_api = True
        if request.content_type and 'application/json' in (request.content_type or ''):
            looks_like_api = True
        if request.method != 'GET':
            looks_like_api = True
        
        if looks_like_api:
            ts = datetime.datetime.utcnow().isoformat() + 'Z'
            entry = {'timestamp': ts, 'remote': remote, 'path': path, 'method': request.method, 'user_agent': ua}
            try:
                api_logger.info(json.dumps(entry))
            except Exception:
                logging.exception('Failed to write api usage log')
    except Exception:
        logging.exception('Error in before_request handler')

# Configure a rotating file logger for API usage
API_USAGE_LOG = os.path.join(LOGS_DIR, 'api_usage.log')
api_logger = logging.getLogger('api_usage')
api_logger.setLevel(logging.INFO)
if not any(isinstance(h, logging.handlers.TimedRotatingFileHandler) for h in api_logger.handlers):
    try:
        handler = logging.handlers.TimedRotatingFileHandler(API_USAGE_LOG, when='W0', interval=1, backupCount=8, encoding='utf-8')
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        api_logger.addHandler(handler)
    except Exception:
        logging.exception('Failed to configure API usage rotating log handler')

# List of DNS servers for selection in the UI
if CUSTOM_DNS_SERVERS_FROM_ENV:
    DNS_SERVERS = CUSTOM_DNS_SERVERS_FROM_ENV
else:
    DNS_SERVERS = [
        "8.8.8.8",    # Google DNS Primary
        "1.1.1.1",    # Cloudflare DNS Primary
        "8.8.4.4",    # Google DNS Secondary
        "1.0.0.1",    # Cloudflare DNS Secondary
    ]

def is_valid_target(target):
    """Check if the target string contains only valid characters for a hostname or IP."""
    return all(c.isalnum() or c in ('.', '-', '_') for c in target)

def is_ip_address(target):
    """Check if the target string is a valid IPv4 or IPv6 address."""
    try:
        ipaddress.ip_address(target)
        return True
    except ValueError:
        return False

def _resolve_hostname_with_fallback(target, dns_server):
    """
    Internal helper to resolve a hostname with all custom logic.
    Returns a tuple: (list_of_ips, notes_string, canonical_name, list_of_aliases)
    """
    try:
        logging.info(f"Resolving hostname '{target}' using DNS server '{dns_server}'")

        lines = []
        
        # Append default domain if it's a single-label hostname and DEFAULT_DOMAIN is set
        if '.' not in target and not is_ip_address(target) and DEFAULT_DOMAIN:
            logging.info(f"Single-label hostname detected. Appending {DEFAULT_DOMAIN}. Original: '{target}', New: '{target}.{DEFAULT_DOMAIN}'")
            lines.append(f"Note: Appending {DEFAULT_DOMAIN} to single-label hostname '{target}'.\n")
            target = f"{target}.{DEFAULT_DOMAIN}"
        
        resolver = dns.resolver.Resolver()
        if dns_server and dns_server != 'System Default':
            if not is_ip_address(dns_server):
                try:
                    dns_server_ip = socket.gethostbyname(dns_server)
                    resolver.nameservers = [dns_server_ip]
                except socket.gaierror:
                    return [], f"Error: Could not resolve DNS server hostname '{dns_server}'", None, []
            else:
                resolver.nameservers = [dns_server]

        canonical = None
        aliases = []
        addresses = []

        # Perform forward lookup, first checking for a CNAME record
        try:
            cname_answers = resolver.resolve(target, 'CNAME', lifetime=5)
            for c in cname_answers:
                cname = str(c.target).rstrip('.')
                canonical = cname
                if target not in aliases:
                    aliases.append(target)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            pass
        except Exception as e:
            logging.warning(f"Unexpected error during CNAME lookup for {target}: {e}")
            pass

        to_resolve = canonical or target

        try:
            a_answers = resolver.resolve(to_resolve, 'A', lifetime=5)
            for a in a_answers:
                ip = str(a)
                if ip not in addresses:
                    addresses.append(ip)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            pass
        except Exception as e:
            logging.warning(f"Unexpected error during A record lookup for {to_resolve}: {e}")
            pass

        return addresses, "\n".join(lines), canonical, aliases

    except Exception as e:
        logging.exception(f"Error in _resolve_hostname_with_fallback for {target}")
        return [], f"Error during DNS resolution: {e}", None, []

def run_nslookup(target, dns_server):
    """
    Main function to perform an nslookup. It uses the internal helper for forward lookups
    and handles reverse (PTR) lookups directly. It formats the final output string.
    """
    try:
        logging.info(f"Running programmatic DNS lookup for {target} using {dns_server}")
        if not target or not is_valid_target(target):
            return "Invalid input."

        if is_ip_address(target):
            resolver = dns.resolver.Resolver()
            if dns_server and dns_server != 'System Default':
                resolver.nameservers = [dns_server]
            reversed_ip = ipaddress.ip_address(target).reverse_pointer
            try:
                ptr_answers = resolver.resolve(reversed_ip, 'PTR', lifetime=5)
                canonical = str(ptr_answers[0].target).rstrip('.')
                return f"Name: {canonical}\nAddress: {target}"
            except Exception as e:
                return f"Name: {target}\nAddress: {target}\nStatus: No reverse DNS (PTR) record found for this IP. ({e})"

        addresses, notes, canonical, aliases = _resolve_hostname_with_fallback(target, dns_server)
        lines = [notes] if notes else []
        display_name = canonical or target
        lines.append(f"Name: {display_name}")
        for ip in addresses:
            lines.append(f"Address: {ip}")

        if aliases:
            lines.append(f"Aliases: {', '.join(aliases)}")

        if not addresses and not canonical:
            lines.append("Status: Hostname does not exist or could not be resolved.")

        return "\n".join(lines)

    except Exception:
        logging.exception("Programmatic DNS lookup failed, falling back to system nslookup.")
        try:
            logging.info(f"Falling back to system nslookup for target: {target} using DNS server: {dns_server}")
            if not target or not is_valid_target(target):
                return "Invalid input."

            command = ['nslookup', target]
            if dns_server and dns_server != "System Default":
                command.append(dns_server)

            return run_subprocess(command, timeout=10)

        except Exception as e:
            return f"An error occurred in fallback nslookup: {str(e)}"

def format_nslookup_output(nslookup_text, query_name=None):
    return nslookup_text

def run_ping(target, count=4):
    """
    Runs a ping command. If the target is a hostname, it first resolves it and then pings the resulting IP.
    """
    PING_TIMEOUT = 5 
    try:
        logging.info(f"Running ping for {target}")
        if not target or not is_valid_target(target):
            return "Invalid input."

        ping_target = target
        resolution_notes = ""

        if not is_ip_address(target):
            addresses, notes, _, _ = _resolve_hostname_with_fallback(target, DNS_SERVERS[0])
            if notes:
                resolution_notes = notes + "\n"
            if addresses:
                ping_target = addresses[0]
                resolution_notes += f"Pinging resolved IP: {ping_target}\n\n"
            else:
                return f"{notes}\nCould not resolve '{target}' to an IP address to ping."

        if platform.system().lower() == "windows":
            command = ['ping', '-n', str(count), ping_target]
        else:
            command = ['ping', '-c', str(count), ping_target]

        ping_output = run_subprocess(command, timeout=PING_TIMEOUT)
        return resolution_notes + ping_output

    except subprocess.TimeoutExpired:
        return f"Ping to {target} timed out after {PING_TIMEOUT} seconds."
    except Exception as e:
        return f"An error occurred in ping: {str(e)}"

def run_dig(target, dig_type='A', dns_server=None):
    """Wrapper for the 'dig' command-line utility."""
    try:
        logging.info(f"Running dig for {target}, type {dig_type}, server {dns_server}")
        if not target or not is_valid_target(target):
            return "Invalid input."

        command = ['dig', target, dig_type]
        if dns_server and dns_server not in ("System Default", "8.8.8.8"):
            command.append(f"@{dns_server}")

        return run_subprocess(command, timeout=10)

    except Exception as e:
        return f"An error occurred in dig: {str(e)}"

def run_traceroute(target):
    """Wrapper for the 'traceroute' or 'tracert' command-line utility."""
    try:
        logging.info(f"Running traceroute for {target}")
        if not target or not is_valid_target(target):
            return "Invalid input."

        note = "Note: This traceroute originates from the application server.\nThe network path shown may differ from the path taken from your local machine or other locations.\n\n"

        if platform.system().lower() == "windows":
            command = ['tracert', target]
        else:
            command = ['traceroute', target]

        traceroute_output = run_subprocess(command, timeout=30)
        return note + traceroute_output

    except Exception as e:
        return f"An error occurred in traceroute: {str(e)}"

def run_test_netconnection(target, port, protocol='tcp'):
    """
    Simulates a port check, similar to Test-NetConnection or nc.
    Currently only supports TCP.
    """
    if protocol.lower() == 'tcp':
        result = run_tcp_connect_test(target, port)
        note = "\n\nNote: Network segmentation or firewalls may cause a port to appear closed (a \"false negative\") even if the service is running."
        return result + note
    elif protocol.lower() == 'udp':
        return "UDP connection test is not easily implemented with standard utilities or Python's socket library in a non-interactive way."
    else:
        return "Unsupported protocol."

def run_tcp_connect_test(target, port):
    """Performs a TCP connection test to a given host and port using a socket."""
    port = int(port)
    logging.info(f"Testing TCP connection to {target}:{port}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    try:
        result = s.connect_ex((target, port))
        if result == 0:
            return f"TCP Connection to {target}:{port} is OPEN."
        else:
            return f"TCP Connection to {target}:{port} is CLOSED or filtered. Error code: {result}"
    except socket.gaierror:
        return f"Hostname {target} could not be resolved."
    except socket.error as e:
        return f"An error occurred during TCP connection test: {e}"
    finally:
        s.close()

def run_subprocess(command, timeout=10):
    """
    A centralized and safe way to run external command-line utilities.
    Captures output, handles timeouts, and provides clear error messages.
    Hides the command window on Windows.
    """
    try:
        startupinfo = None
        if platform.system().lower() == "windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        result = subprocess.check_output(
            command,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            timeout=timeout,
            startupinfo=startupinfo
        )
        return result
    except FileNotFoundError:
        return f"Error: Command '{command[0]}' not found on the system."
    except subprocess.CalledProcessError as e:
        logging.warning(f"Subprocess failed: {e.output.strip()}")
        return f"Command failed:\n{e.output.strip()}"
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds."
    except Exception as e:
        logging.exception(f"Unexpected error running subprocess: {' '.join(command)}")
        return f"An unexpected error occurred: {str(e)}"

def run_reverse_lookup(ip_address, dns_server):
    """
    Performs a reverse DNS (PTR) lookup for a given IP address.
    Used by the bulk lookup tool.
    """
    try:
        resolver = dns.resolver.Resolver()
        if dns_server and dns_server != 'System Default':
            resolver.nameservers = [dns_server]

        if ipaddress.ip_address(ip_address).version == 4:
            reversed_ip = '.'.join(ip_address.split('.')[::-1]) + '.in-addr.arpa'
        else:
            reversed_ip = ipaddress.ip_address(ip_address).reverse_pointer

        ptr_answers = resolver.resolve(reversed_ip, 'PTR', lifetime=5)
        for ptr in ptr_answers:
            return str(ptr.target).rstrip('.')
        return "No PTR record"
    except dns.resolver.NXDOMAIN:
        return "No PTR record (NXDOMAIN)"
    except Exception as e:
        logging.warning(f"Reverse lookup for {ip_address} failed: {e}")
        return "Error"

def run_bulk_nslookup(file_storage, dns_server, should_ping, should_reverse_lookup):
    """
    Processes an uploaded CSV file of hostnames.
    Performs nslookup on each, with optional ping and reverse lookup,
    and returns the results as a CSV-formatted string.
    """
    results = []
    temp_path = None
    try:
        temp_filename = str(uuid.uuid4()) + '.csv'
        temp_path = os.path.join(BULK_RESULTS_DIR, temp_filename)
        file_storage.save(temp_path)

        with open(temp_path, 'r') as f:
            content = f.read()

        targets = []
        for line in content.splitlines():
            targets.extend([t.strip() for t in re.split(r'[,\s]+', line) if t.strip()])

        targets = [t for t in targets if is_valid_target(t)]

        output_data = []
        output_data.append("Target,Resolved_Name,Resolved_IP,Ping_Result,Reverse_Lookup_PTR")

        for target in targets:
            ns_result_text = run_nslookup(target, dns_server)
            ip_matches = re.findall(r'Address: ([\d\.]+)', ns_result_text)
            
            ips_str = '; '.join(ip_matches) if ip_matches else 'N/A'
            first_ip = ip_matches[0] if ip_matches else 'N/A'

            name_match = re.search(r'Name: (.+)', ns_result_text)
            name = name_match.group(1).strip() if name_match else 'N/A'

            ping_result = 'N/A'
            if should_ping and first_ip != 'N/A':
                ping_output = run_ping(first_ip, count=1)
                ping_match = re.search(r'TTL=\d+', ping_output)
                ping_result = 'Success' if ping_match else 'Failed'
            
            ptr_record = 'N/A'
            if should_reverse_lookup and first_ip != 'N/A':
                ptr_record = run_reverse_lookup(first_ip, dns_server)

            output_data.append(f'"{target}","{name}","{ips_str}","{ping_result}","{ptr_record}"')

        bulk_output = "\n".join(output_data)

        output_filename = 'bulk_nslookup_result_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv'
        session['bulk_file'] = output_filename

        final_path = os.path.join(BULK_RESULTS_DIR, output_filename)
        with open(final_path, 'w') as f:
            f.write(bulk_output)

        return bulk_output

    except Exception as e:
        logging.exception("Error during bulk NSLookup processing")
        return f"An error occurred during bulk processing: {str(e)}"
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

# --- API Routes for Programmatic Access ---

@app.route('/api/nslookup', methods=['GET', 'POST'])
def api_nslookup():
    """
    API endpoint for NSLookup queries.
    GET: ?target=hostname&dns_server=8.8.8.8 (dns_server optional)
    POST: {"target": "hostname", "dns_server": "8.8.8.8"} (dns_server optional)
    """
    if request.method == 'POST':
        data = request.get_json() or {}
        target = data.get('target', '').strip()
        dns_server = data.get('dns_server', DNS_SERVERS[0]).strip()
    else:
        target = request.args.get('target', '').strip()
        dns_server = request.args.get('dns_server', DNS_SERVERS[0]).strip()
    
    if not target:
        return jsonify({"error": "Target parameter required"}), 400
    
    if not is_valid_target(target):
        return jsonify({"error": "Invalid target format"}), 400
    
    result = run_nslookup(target, dns_server)
    
    return jsonify({
        "success": True,
        "target": target,
        "dns_server": dns_server,
        "result": result,
        "timestamp": datetime.datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/api/ping', methods=['GET', 'POST'])
def api_ping():
    """
    API endpoint for Ping queries.
    GET: ?target=hostname&count=4
    POST: {"target": "hostname", "count": 4}
    """
    if request.method == 'POST':
        data = request.get_json() or {}
        target = data.get('target', '').strip()
        count = int(data.get('count', 4))
    else:
        target = request.args.get('target', '').strip()
        count = int(request.args.get('count', 4))
    
    if not target:
        return jsonify({"error": "Target parameter required"}), 400
    
    if not is_valid_target(target):
        return jsonify({"error": "Invalid target format"}), 400
    
    result = run_ping(target, count=count)
    
    return jsonify({
        "success": True,
        "target": target,
        "count": count,
        "result": result,
        "timestamp": datetime.datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/api/dig', methods=['GET', 'POST'])
def api_dig():
    """
    API endpoint for Dig queries.
    GET: ?target=hostname&type=A&dns_server=8.8.8.8
    POST: {"target": "hostname", "type": "A", "dns_server": "8.8.8.8"}
    """
    if request.method == 'POST':
        data = request.get_json() or {}
        target = data.get('target', '').strip()
        dig_type = data.get('type', 'A').strip().upper()
        dns_server = data.get('dns_server', None)
    else:
        target = request.args.get('target', '').strip()
        dig_type = request.args.get('type', 'A').strip().upper()
        dns_server = request.args.get('dns_server', None)
    
    if not target:
        return jsonify({"error": "Target parameter required"}), 400
    
    if not is_valid_target(target):
        return jsonify({"error": "Invalid target format"}), 400
    
    result = run_dig(target, dig_type=dig_type, dns_server=dns_server)
    
    return jsonify({
        "success": True,
        "target": target,
        "type": dig_type,
        "dns_server": dns_server or "System Default",
        "result": result,
        "timestamp": datetime.datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/api/traceroute', methods=['GET', 'POST'])
def api_traceroute():
    """
    API endpoint for Traceroute queries.
    GET: ?target=hostname
    POST: {"target": "hostname"}
    """
    if request.method == 'POST':
        data = request.get_json() or {}
        target = data.get('target', '').strip()
    else:
        target = request.args.get('target', '').strip()
    
    if not target:
        return jsonify({"error": "Target parameter required"}), 400
    
    if not is_valid_target(target):
        return jsonify({"error": "Invalid target format"}), 400
    
    result = run_traceroute(target)
    
    return jsonify({
        "success": True,
        "target": target,
        "result": result,
        "timestamp": datetime.datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/api/netconnection', methods=['GET', 'POST'])
def api_netconnection():
    """
    API endpoint for Network Connection testing.
    GET: ?target=hostname&port=443&protocol=tcp
    POST: {"target": "hostname", "port": 443, "protocol": "tcp"}
    """
    if request.method == 'POST':
        data = request.get_json() or {}
        target = data.get('target', '').strip()
        port = int(data.get('port', 443))
        protocol = data.get('protocol', 'tcp').lower()
    else:
        target = request.args.get('target', '').strip()
        port = int(request.args.get('port', 443))
        protocol = request.args.get('protocol', 'tcp').lower()
    
    if not target:
        return jsonify({"error": "Target parameter required"}), 400
    
    if not is_valid_target(target):
        return jsonify({"error": "Invalid target format"}), 400
    
    result = run_test_netconnection(target, port, protocol)
    
    return jsonify({
        "success": True,
        "target": target,
        "port": port,
        "protocol": protocol,
        "result": result,
        "timestamp": datetime.datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/api/docs')
def api_docs():
    """API documentation page."""
    return render_template('api_docs.html',
                         dns_servers=DNS_SERVERS,
                         status_check_host=STATUS_CHECK_HOST,
                         is_development=FLASK_ENV == 'development',
                         canonical_host=CANONICAL_HOST)

# --- Flask Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route for the application. Handles both GET requests for the page and POST requests from the tool form."""
    context = {
        'target': '',
        'tool': 'nslookup',
        'dns_server': DNS_SERVERS[0],
        'dig_type': 'A',
        'port': '443',
        'port_protocol': 'tcp',
        'nslookup_then_ping': False,
        'result': None,
        'bulk_results': None
    }

    if request.method == 'POST':
        try:
            target = request.form.get('target-name', '').strip()
            tool = request.form.get('tool-name', 'nslookup')
            dns_server = request.form.get('dns-server', context['dns_server'])
            dig_type = request.form.get('dig-type', context['dig_type'])
            port = request.form.get('port-number', context['port'])
            port_protocol = request.form.get('port-protocol', context['port_protocol'])
            nslookup_then_ping = request.form.get('nslookup-then-ping') == '1'

            context.update({
                'target': target,
                'tool': tool,
                'dns_server': dns_server,
                'dig_type': dig_type,
                'port': port,
                'port_protocol': port_protocol,
                'nslookup_then_ping': nslookup_then_ping
            })

            result = "Error: Unknown tool."

            if not target and tool != 'bulk-nslookup':
                result = "Error: Target hostname/IP cannot be empty."
            elif not is_valid_target(target) and tool != 'bulk-nslookup':
                result = "Error: Invalid characters in target name."
            else:
                if tool == 'nslookup':
                    result = run_nslookup(target, dns_server)
                    if nslookup_then_ping:
                        ip_match = re.search(r'Address: ([\d\.]+)', result)
                        ip_to_ping = ip_match.group(1) if ip_match else None

                        ping_result = "Ping skipped (No IP found)."
                        if ip_to_ping:
                            ping_output = run_ping(ip_to_ping, count=4)
                            ping_result = f"\n\n--- Ping Result for {ip_to_ping} ---\n{ping_output}"

                        result += ping_result

                elif tool == 'ping':
                    result = run_ping(target)
                elif tool == 'dig':
                    result = run_dig(target, dig_type, dns_server)
                elif tool == 'traceroute':
                    result = run_traceroute(target)
                elif tool == 'test-netconnection':
                    if not port.isdigit() or not (1 <= int(port) <= 65535):
                        result = "Error: Port number must be between 1 and 65535."
                    else:
                        result = run_test_netconnection(target, port, port_protocol)
                elif tool == 'bulk-nslookup':
                    pass

            context['result'] = result

        except Exception:
            logging.exception("Error processing form submission")
            context['result'] = "An unexpected server error occurred."

    context.update({
        'dns_servers': DNS_SERVERS,
        'status_check_host': STATUS_CHECK_HOST,
        'is_development': FLASK_ENV == 'development',
        'canonical_host': CANONICAL_HOST
    })

    return render_template('index.html', **context)

@app.route('/bulk-nslookup', methods=['POST'])
def bulk_nslookup_route():
    """Route specifically for handling the bulk nslookup file upload."""
    file_storage = request.files.get('csvfile')    
    bulk_dns_server = request.form.get('bulk-dns-server', DNS_SERVERS[0])
    bulk_then_ping = request.form.get('bulk-ping') == 'on'
    should_reverse_lookup = request.form.get('bulk-reverse') == 'on'

    if not file_storage:
        return render_template('index.html', 
                             result="Error: No file uploaded.", 
                             tool='bulk-nslookup',
                             dns_servers=DNS_SERVERS,
                             status_check_host=STATUS_CHECK_HOST,
                             is_development=FLASK_ENV == 'development',
                             canonical_host=CANONICAL_HOST)

    bulk_results = run_bulk_nslookup(file_storage, bulk_dns_server, bulk_then_ping, should_reverse_lookup)

    return render_template(
        'index.html',
        tool='bulk-nslookup',
        bulk_results=bulk_results,
        dns_server=bulk_dns_server,
        dns_servers=DNS_SERVERS,
        status_check_host=STATUS_CHECK_HOST,
        is_development=FLASK_ENV == 'development',
        canonical_host=CANONICAL_HOST
    )

@app.route('/download-bulk')
def download_bulk():
    """
    Provides the generated bulk results file for download.
    Retrieves the filename from the session, reads the file, and serves it as a download.
    """
    filename = session.get('bulk_file')
    if not filename:
        return "No bulk result file found.", 404

    file_path = os.path.join(BULK_RESULTS_DIR, filename)
    if not os.path.exists(file_path):
        return "Bulk result file not found on disk.", 404

    try:
        return Response(
            open(file_path, 'rb').read(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment;filename={filename}'}
        )
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            if 'bulk_file' in session:
                session.pop('bulk_file')

@app.route('/api/dns-status')
def dns_status():
    """
    An API endpoint to check the status of the configured STATUS_CHECK_HOST.
    It caches the result in the user's session for the configured interval to avoid excessive checks.
    The frontend polls this endpoint to display the status.
    """
    target = STATUS_CHECK_HOST
    last_checked = session.get('dns_last_checked', 0)
    status_message = session.get('dns_status_message', "Checking status...")
    is_online = session.get('dns_is_online', False)

    current_time = datetime.datetime.now().timestamp()
    if current_time - last_checked > STATUS_CHECK_INTERVAL or last_checked == 0:

        logging.info(f"Performing fresh status check for {target}")

        ping_output = run_ping(target, count=1)

        if "time=" in ping_output.lower() or "ttl=" in ping_output.lower() or "bytes=" in ping_output.lower():
            is_online = True
            status_message = f"✅ {target} is ONLINE"
        else:
            is_online = False
            status_message = f"❌ {target} is OFFLINE or unreachable"

        session['dns_last_checked'] = current_time
        session['dns_status_message'] = status_message
        session['dns_is_online'] = is_online
        last_checked = current_time

    return jsonify({
        "online": is_online,
        "message": status_message,
        "last_checked": last_checked
    })

if __name__ == '__main__':
    """
    Main execution block. This code runs when the script is executed directly.
    It handles virtual environment creation, dependency installation, and starts
    the production-ready Waitress web server.
    """
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    print(f"=== Network Diagnostics Tool Configuration ===")
    print(f"Environment: {FLASK_ENV}")
    print(f"Port: {APP_PORT}")
    print(f"Canonical Host: {CANONICAL_HOST}")
    print(f"Status Check Host: {STATUS_CHECK_HOST}")
    print(f"DNS Servers: {len(DNS_SERVERS)} configured")
    print(f"===============================================")
    print(f"Starting Flask application on http://0.0.0.0:{APP_PORT}...")
    
    if FLASK_ENV == 'development':
        app.run(host="0.0.0.0", port=APP_PORT, debug=True)
    else:
        from waitress import serve
        serve(app, host="0.0.0.0", port=APP_PORT, threads=25)
