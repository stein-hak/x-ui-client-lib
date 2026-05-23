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

### Batch Operations (High Performance)

```python
# Batch add clients to single inbound
success, count = client.batch_add_clients_to_inbound(
    inbound_id=1,
    clients=clients,
    merge_with_existing=True
)

# Batch sync to all VLESS inbounds
results = client.batch_sync_clients_to_all_vless_inbounds(clients)

# Clone inbound to another node
new_inbound = client.clone_inbound_to_node(1, target_client, new_port=443)
```

## Requirements

- Python 3.6+
- requests >= 2.25.0

## License

MIT License
