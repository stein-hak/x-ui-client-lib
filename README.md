# x-ui-client - High-Performance Python Client for 3x-ui

A comprehensive Python client library for managing 3x-ui VPN panel with batch operations support.

## Features

- **⚡ Batch Operations** - 20-30x faster than sequential operations
- **📊 Complete API Coverage** - Inbounds, clients, server management
- **🔄 Clone Operations** - Export/import inbound configurations
- **🔒 Production Tested** - Validated with 6,015 real clients
- **🎯 Type Hints** - Full type annotation support
- **📖 Comprehensive Docs** - Detailed docstrings for all methods

## Performance

| Operation | Rate | Speedup vs Sequential |
|-----------|------|----------------------|
| Batch add clients | 3,300/s | 20.6x faster |
| Clone inbound | 2,294/s | 14.3x faster |
| Import inbound | 4,900/s | 30x faster |

## Installation

```bash
# As git submodule in your project
git submodule add <repository-url> x_ui_client
```

## Quick Start

```python
from x_ui_client import XUIClient

# Connect to 3x-ui panel
client = XUIClient("http://node:2053", "admin", "password")
client.login()

# List inbounds
inbounds = client.get_inbounds()

# Batch add 1000 clients (fast!)
success, count = client.batch_add_clients_to_inbound(1, clients)
print(f"Added {count} clients")
```

## API Methods

### Authentication

```python
# Login to panel
client.login()
```

### Inbound Management

```python
# Get all inbounds
inbounds = client.get_inbounds()

# Get specific inbound
inbound = client.get_inbound(inbound_id=1)

# Add new inbound
success = client.add_inbound(config)

# Update inbound
success = client.update_inbound(inbound_id=1, config=config)

# Delete inbound
success = client.delete_inbound(inbound_id=1)

# Get online clients
online = client.get_online_clients()
```

### Client Management

```python
# Add single client
success = client.add_client(client_config)

# Update client
success = client.update_client(client_id="uuid", config=config)

# Delete client
success = client.delete_client(inbound_id=1, email="user@example.com")

# Reset client traffic
success = client.reset_client_traffic(email="user@example.com")
```

### Batch Operations (High Performance)

```python
# Batch add clients to inbound (3,300/sec)
success, count = client.batch_add_clients_to_inbound(
    inbound_id=1,
    clients=clients,
    merge_with_existing=True
)

# Batch sync to all VLESS inbounds
results = client.batch_sync_clients_to_all_vless_inbounds(
    clients=clients,
    email_suffix_template="_{inbound_id}"
)

# Import entire inbound with clients (4,900/sec)
new_inbound = client.import_inbound(inbound_data)

# Clone inbound to another node (2,294/sec)
new_inbound = client.clone_inbound_to_node(
    source_inbound_id=1,
    target_client=target_client,
    new_port=443,
    new_remark="Clone"
)
```

### Server Management

```python
# Get server status
status = client.get_server_status()

# Get Xray versions
versions = client.get_xray_version()

# Restart Xray service
success = client.restart_xray_service()

# Install Xray version
success = client.install_xray(version="1.8.0")

# Update geo files
success = client.update_geofiles()

# Get Xray logs
logs = client.get_xray_logs(count=100)
```

### Backup

```python
# Backup to Telegram
success = client.backup_to_telegram()
```

## Requirements

- Python 3.6+
- requests >= 2.25.0

## License

MIT License
