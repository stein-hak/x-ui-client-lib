"""
Main 3x-ui API client implementation
"""

import requests
import json
from typing import Optional, Dict, List, Any, Tuple
from .exceptions import AuthenticationError, APIError, NotFoundError


class XUIClient:
    """Client for interacting with 3x-ui panel API"""

    def __init__(self, base_url: str, username: str, password: str, verify_ssl: bool = True):
        """
        Initialize the 3x-ui API client

        Args:
            base_url: Base URL of the 3x-ui panel (e.g., 'http://localhost:2053')
            username: Admin username
            password: Admin password
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self._authenticated = False
        self._csrf_token = None

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an API request

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (will be appended to base_url)
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response JSON data

        Raises:
            APIError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault('verify', self.verify_ssl)

        # Add CSRF token to POST/PUT/DELETE requests (v3.0.0+)
        if method.upper() in ('POST', 'PUT', 'DELETE') and self._csrf_token:
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            kwargs['headers']['X-CSRF-Token'] = self._csrf_token

        try:
            response = self.session.request(method, url, **kwargs)

            # Handle different status codes
            if response.status_code == 404:
                raise NotFoundError("Resource not found", status_code=404, response=response)
            elif response.status_code == 401:
                raise AuthenticationError("Authentication required or session expired")
            elif not response.ok:
                raise APIError(
                    f"API request failed: {response.status_code}",
                    status_code=response.status_code,
                    response=response
                )

            # Try to parse JSON response
            try:
                return response.json()
            except ValueError:
                return {"success": True, "data": response.text}

        except requests.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")

    def _get_csrf_token(self) -> Optional[str]:
        """
        Get CSRF token (required for v3.0.0+)

        Returns:
            CSRF token string or None if not supported
        """
        try:
            response = self._make_request('GET', '/csrf-token')
            return response.get('obj') or response.get('csrfToken')
        except (APIError, NotFoundError):
            # Old version without CSRF support
            return None

    def login(self) -> bool:
        """
        Authenticate with the 3x-ui panel
        Supports both old versions (without CSRF) and new versions (v3.0.0+ with CSRF)

        Returns:
            True if authentication successful

        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            # Try to get CSRF token (v3.0.0+)
            csrf_token = self._get_csrf_token()
            if csrf_token:
                self._csrf_token = csrf_token

            # Prepare login data
            login_data = {
                'username': self.username,
                'password': self.password
            }

            # Prepare headers
            headers = {'Content-Type': 'application/json'}
            if csrf_token:
                headers['X-CSRF-Token'] = csrf_token

            # Attempt login
            response = self._make_request(
                'POST',
                '/login',
                json=login_data,
                headers=headers
            )

            if response.get('success'):
                self._authenticated = True
                return True
            else:
                raise AuthenticationError("Login failed: Invalid credentials")

        except APIError as e:
            # If 403 and we didn't use CSRF, it might be old form-data format
            if e.status_code == 403 and not csrf_token:
                try:
                    # Retry with form data (old API format)
                    response = self._make_request(
                        'POST',
                        '/login',
                        data=login_data
                    )
                    if response.get('success'):
                        self._authenticated = True
                        return True
                except:
                    pass

            raise AuthenticationError(f"Login failed: {str(e)}")

    def _ensure_authenticated(self):
        """Ensure the client is authenticated, login if needed"""
        if not self._authenticated:
            self.login()

    # ========== Inbound Management ==========

    def get_inbounds(self) -> List[Dict[str, Any]]:
        """
        Get list of all inbounds

        Returns:
            List of inbound configurations
        """
        self._ensure_authenticated()
        response = self._make_request('GET', '/panel/api/inbounds/list')
        return response.get('obj') or []

    def get_inbound(self, inbound_id: int) -> Dict[str, Any]:
        """
        Get specific inbound by ID

        Args:
            inbound_id: ID of the inbound

        Returns:
            Inbound configuration
        """
        self._ensure_authenticated()
        response = self._make_request('GET', f'/panel/api/inbounds/get/{inbound_id}')
        return response.get('obj', {})

    def add_inbound(self, config: Dict[str, Any]) -> bool:
        """
        Add a new inbound

        Args:
            config: Inbound configuration dictionary

        Returns:
            True if successful
        """
        self._ensure_authenticated()
        response = self._make_request('POST', '/panel/api/inbounds/add', json=config)
        return response.get('success', False)

    def update_inbound(self, inbound_id: int, config: Dict[str, Any]) -> bool:
        """
        Update an existing inbound

        Args:
            inbound_id: ID of the inbound to update
            config: Inbound configuration dictionary

        Returns:
            True if successful
        """
        self._ensure_authenticated()
        response = self._make_request('POST', f'/panel/api/inbounds/update/{inbound_id}', json=config)
        return response.get('success', False)

    def delete_inbound(self, inbound_id: int) -> bool:
        """
        Delete an inbound

        Args:
            inbound_id: ID of the inbound to delete

        Returns:
            True if successful
        """
        self._ensure_authenticated()
        response = self._make_request('POST', f'/panel/api/inbounds/del/{inbound_id}')
        return response.get('success', False)

    def get_online_clients(self) -> List[str]:
        """
        Get list of currently online clients

        Returns:
            List of online client emails
        """
        self._ensure_authenticated()
        response = self._make_request('POST', '/panel/api/inbounds/onlines')
        return response.get('obj') or []

    # ========== Client Management ==========

    def add_client(self, client_config: Dict[str, Any]) -> bool:
        """
        Add a client to an inbound

        Args:
            client_config: Client configuration dictionary

        Returns:
            True if successful
        """
        self._ensure_authenticated()
        response = self._make_request('POST', '/panel/api/inbounds/addClient', json=client_config)
        return response.get('success', False)

    def update_client(self, client_id: str, config: Dict[str, Any]) -> bool:
        """
        Update client settings

        Args:
            client_id: Client UUID
            config: Updated client configuration

        Returns:
            True if successful
        """
        self._ensure_authenticated()
        response = self._make_request('POST', f'/panel/api/inbounds/updateClient/{client_id}', json=config)
        return response.get('success', False)

    def delete_client(self, inbound_id: int, email: str) -> bool:
        """
        Delete a client by email

        Args:
            inbound_id: Inbound ID
            email: Client email

        Returns:
            True if successful
        """
        self._ensure_authenticated()
        response = self._make_request('POST', f'/panel/api/inbounds/{inbound_id}/delClientByEmail/{email}')
        return response.get('success', False)

    def reset_client_traffic(self, email: str) -> bool:
        """
        Reset client traffic statistics

        Args:
            email: Client email

        Returns:
            True if successful
        """
        self._ensure_authenticated()
        response = self._make_request('POST', f'/panel/api/inbounds/resetClientTraffic/{email}')
        return response.get('success', False)

    # ========== Batch Client Operations (High Performance) ==========

    def batch_add_clients_to_inbound(
        self,
        inbound_id: int,
        clients: List[Dict[str, Any]],
        merge_with_existing: bool = True
    ) -> Tuple[bool, int]:
        """
        Add multiple clients to an inbound in a single request (batch operation).

        This is MUCH faster than calling add_client() for each client sequentially.
        Performance: ~3,300 clients/sec vs ~160 clients/sec for sequential.

        Args:
            inbound_id: ID of the inbound to add clients to
            clients: List of client configurations. Each client dict should contain:
                - id: Client UUID (required)
                - email: Client email (required, must be globally unique)
                - flow: Flow control (usually "")
                - limitIp: IP limit (0 for unlimited)
                - totalGB: Total bandwidth in GB (0 for unlimited)
                - expiryTime: Expiry timestamp in ms (0 for never)
                - enable: Whether client is enabled (True/False)
                - tgId: Telegram ID (optional, "" or 0)
                - subId: Subscription ID (optional, usually same as email)
            merge_with_existing: If True, merge with existing clients.
                                If False, replace all existing clients.

        Returns:
            Tuple of (success: bool, num_clients_added: int)

        Example:
            ```python
            clients = [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user1@example.com",
                    "flow": "",
                    "limitIp": 0,
                    "totalGB": 0,
                    "expiryTime": 0,
                    "enable": True,
                    "tgId": "",
                    "subId": "user1@example.com"
                },
                # ... more clients
            ]
            success, count = client.batch_add_clients_to_inbound(1, clients)
            print(f"Added {count} clients")
            ```
        """
        self._ensure_authenticated()

        # Get current inbound configuration
        inbound = self.get_inbound(inbound_id)
        if not inbound:
            raise NotFoundError(f"Inbound {inbound_id} not found")

        # Parse existing settings
        settings = json.loads(inbound.get("settings", "{}"))
        existing_clients = settings.get("clients", [])

        # Merge or replace
        if merge_with_existing:
            settings["clients"] = existing_clients + clients
        else:
            settings["clients"] = clients

        # Update inbound with new clients
        inbound["settings"] = json.dumps(settings)

        response = self._make_request(
            'POST',
            f'/panel/api/inbounds/update/{inbound_id}',
            json=inbound,
            timeout=60  # Longer timeout for large batches
        )

        success = response.get('success', False)
        num_added = len(clients) if success else 0

        return success, num_added

    def batch_sync_clients_to_all_vless_inbounds(
        self,
        clients: List[Dict[str, Any]],
        email_suffix_template: str = "_{inbound_id}"
    ) -> Dict[int, Tuple[bool, int]]:
        """
        Sync clients to ALL VLESS inbounds on this node in batch mode.

        This is the optimal method for provisioning a new node with many clients.
        Each inbound is updated in a single request.

        Args:
            clients: List of client configurations (see batch_add_clients_to_inbound)
            email_suffix_template: Template for making emails unique per inbound.
                                  Use {inbound_id} as placeholder. Default: "_{inbound_id}"

        Returns:
            Dictionary mapping inbound_id -> (success, num_clients_added)

        Example:
            ```python
            clients = [...]  # 7,205 clients
            results = client.batch_sync_clients_to_all_vless_inbounds(clients)

            for inbound_id, (success, count) in results.items():
                print(f"Inbound {inbound_id}: {'✓' if success else '✗'} ({count} clients)")
            ```
        """
        self._ensure_authenticated()

        # Get all VLESS inbounds
        all_inbounds = self.get_inbounds()
        vless_inbounds = [ib for ib in all_inbounds if ib.get("protocol") == "vless"]

        results = {}

        for inbound in vless_inbounds:
            inbound_id = inbound["id"]

            # Create unique emails for this inbound
            inbound_clients = []
            for client in clients:
                client_copy = client.copy()

                # Apply email suffix to make it unique per inbound
                base_email = client["email"]
                suffix = email_suffix_template.format(inbound_id=inbound_id)
                client_copy["email"] = f"{base_email}{suffix}"

                # Also update subId if it exists
                if "subId" in client_copy:
                    client_copy["subId"] = client_copy["email"]

                inbound_clients.append(client_copy)

            # Batch add to this inbound
            try:
                success, count = self.batch_add_clients_to_inbound(
                    inbound_id,
                    inbound_clients,
                    merge_with_existing=True
                )
                results[inbound_id] = (success, count)
            except Exception as e:
                results[inbound_id] = (False, 0)

        return results

    def import_inbound(self, inbound_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Import an inbound configuration (creates a new inbound with all clients).

        This is the fastest way to clone an entire inbound with all its clients.
        Performance: ~4,900 clients/sec

        WARNING: Email addresses must be globally unique across all inbounds.
        If the source inbound still exists, you'll get duplicate email errors.

        Args:
            inbound_data: Complete inbound configuration (from get_inbound())

        Returns:
            Created inbound object, or None if failed

        Example:
            ```python
            # Export from source node
            source_client = XUIClient("http://source:2053", "admin", "pass")
            source_client.login()
            inbound = source_client.get_inbound(1)

            # Import to target node
            target_client = XUIClient("http://target:2053", "admin", "pass")
            target_client.login()
            new_inbound = target_client.import_inbound(inbound)
            ```
        """
        self._ensure_authenticated()

        response = self._make_request(
            'POST',
            '/panel/api/inbounds/import',
            data={"data": json.dumps(inbound_data)},
            timeout=60
        )

        return response.get('obj') if response.get('success') else None

    def clone_inbound_to_node(
        self,
        source_inbound_id: int,
        target_client: 'XUIClient',
        new_port: Optional[int] = None,
        new_remark: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Clone an inbound from this node to another node.

        This is useful for disaster recovery or creating identical nodes.

        Args:
            source_inbound_id: ID of inbound to clone
            target_client: Authenticated XUIClient for target node
            new_port: Optional new port for cloned inbound
            new_remark: Optional new remark/name for cloned inbound

        Returns:
            Created inbound object on target node, or None if failed

        Example:
            ```python
            source = XUIClient("http://source:2053", "admin", "pass")
            target = XUIClient("http://target:2053", "admin", "pass")
            source.login()
            target.login()

            # Clone inbound 1 from source to target
            new_inbound = source.clone_inbound_to_node(1, target, new_port=443)
            ```
        """
        self._ensure_authenticated()

        # Export from source
        inbound_data = self.get_inbound(source_inbound_id)
        if not inbound_data:
            return None

        # Modify port/remark if specified
        if new_port is not None:
            inbound_data["port"] = new_port
        if new_remark is not None:
            inbound_data["remark"] = new_remark

        # Import to target
        return target_client.import_inbound(inbound_data)

    # ========== Server Management ==========

    def get_server_status(self) -> Dict[str, Any]:
        """
        Get server status information

        Returns:
            Server status data
        """
        self._ensure_authenticated()
        response = self._make_request('GET', '/panel/api/server/status')
        return response.get('obj', {})

    def get_xray_version(self) -> List[str]:
        """
        Get available Xray versions

        Returns:
            List of available versions
        """
        self._ensure_authenticated()
        response = self._make_request('GET', '/panel/api/server/getXrayVersion')
        return response.get('obj') or []

    def restart_xray_service(self) -> bool:
        """
        Restart Xray service

        Returns:
            True if successful
        """
        self._ensure_authenticated()
        response = self._make_request('POST', '/panel/api/server/restartXrayService')
        return response.get('success', False)

    def install_xray(self, version: str) -> bool:
        """
        Install specific Xray version

        Args:
            version: Version to install

        Returns:
            True if successful
        """
        self._ensure_authenticated()
        response = self._make_request('POST', f'/panel/api/server/installXray/{version}')
        return response.get('success', False)

    def update_geofiles(self) -> bool:
        """
        Update geographic database files

        Returns:
            True if successful
        """
        self._ensure_authenticated()
        response = self._make_request('POST', '/panel/api/server/updateGeofile')
        return response.get('success', False)

    def get_xray_logs(self, count: int = 100) -> str:
        """
        Get Xray service logs

        Args:
            count: Number of log lines to retrieve

        Returns:
            Log content as string
        """
        self._ensure_authenticated()
        response = self._make_request('POST', f'/panel/api/server/xraylogs/{count}')
        return response.get('obj', '')

    # ========== Backup ==========

    def backup_to_telegram(self) -> bool:
        """
        Backup configuration to Telegram bot

        Returns:
            True if successful
        """
        self._ensure_authenticated()
        response = self._make_request('GET', '/panel/api/backuptotgbot')
        return response.get('success', False)
