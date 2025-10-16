"""
Docker Manager - Container discovery, control, and UI detection
"""
import docker
import re
from typing import List, Dict, Optional
from pydantic import BaseModel


class ContainerInfo(BaseModel):
    """Container information model"""
    id: str
    name: str
    image: str
    status: str
    state: str
    ports: List[Dict[str, str]] = []
    web_url: Optional[str] = None
    labels: Dict[str, str] = {}
    created: str = ""
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    networks: List[str] = []
    network_mode: str = ""
    volumes: List[Dict[str, str]] = []
    volume_size_mb: float = 0.0
    memory_usage_mb: float = 0.0
    memory_limit_mb: float = 0.0
    memory_percent: float = 0.0
    cpu_percent: float = 0.0
    restart_count: int = 0
    health_status: Optional[str] = None


class DockerManager:
    """Manages Docker container inspection and control"""

    # Known web UI patterns (name_pattern: default_port)
    WEB_UI_PATTERNS = {
        r'portainer': 9443,
        r'gitea': 3000,
        r'n8n': 5678,
        r'node-red': 1880,
        r'beszel': 4590,
        r'grafana': 3000,
        r'prometheus': 9090,
        r'jupyter': 8888,
        r'vscode|code-server': 8443,
        r'heimdall|homer': 80,
        r'sonarr|radarr|lidarr': 8989,
        r'plex': 32400,
        r'emby|jellyfin': 8096,
        r'nginx-proxy-manager': 81,
        r'traefik': 8080,
        r'adguard': 80,
        r'pihole': 80,
        r'uptime-kuma': 3001,
        r'ghost': 2368,
        r'wordpress': 80,
        r'nextcloud': 80,
    }

    def __init__(self):
        try:
            self.client = docker.DockerClient(base_url='unix://var/run/docker.sock')
            self.client.ping()
        except Exception as e:
            print(f"Docker client initialization failed: {e}")
            self.client = None

    async def get_containers(self, include_stats: bool = False) -> List[ContainerInfo]:
        """Get all containers with web UI detection

        Args:
            include_stats: If True, collect CPU/memory stats (slow for many containers)
        """
        if not self.client:
            return []

        containers = []
        for container in self.client.containers.list(all=True):
            info = self._extract_container_info(container, include_stats=include_stats)
            containers.append(info)

        return containers

    def _extract_container_info(self, container, include_stats: bool = False) -> ContainerInfo:
        """Extract container information with UI detection

        Args:
            include_stats: If True, collect CPU/memory stats (slow operation)
        """
        attrs = container.attrs
        state = attrs.get('State', {})
        config = attrs.get('Config', {})
        host_config = attrs.get('HostConfig', {})

        # Get port mappings
        ports = self._parse_ports(container)

        # Detect web UI
        web_url = self._detect_web_ui(container.name, ports, container.labels)

        # Get network information
        networks = list(attrs.get('NetworkSettings', {}).get('Networks', {}).keys())
        network_mode = host_config.get('NetworkMode', 'bridge')

        # Get volume information
        mounts = attrs.get('Mounts', [])
        volumes = [
            {
                'name': m.get('Name', m.get('Source', 'unknown')),
                'destination': m.get('Destination', ''),
                'type': m.get('Type', 'bind'),
                'rw': 'rw' if m.get('RW', True) else 'ro'
            }
            for m in mounts
        ]

        # Get timestamps
        created = attrs.get('Created', '')
        started_at = state.get('StartedAt', '')
        finished_at = state.get('FinishedAt', '') if state.get('Status') != 'running' else None

        # Get resource stats (requires stats API call - SLOW!)
        memory_usage_mb = 0.0
        memory_limit_mb = 0.0
        memory_percent = 0.0
        cpu_percent = 0.0

        if include_stats:
            try:
                if container.status == 'running':
                    stats = container.stats(stream=False)
                    # Memory stats
                    mem_stats = stats.get('memory_stats', {})
                    memory_usage_mb = mem_stats.get('usage', 0) / (1024 * 1024)
                    memory_limit_mb = mem_stats.get('limit', 0) / (1024 * 1024)
                    if memory_limit_mb > 0:
                        memory_percent = (memory_usage_mb / memory_limit_mb) * 100

                    # CPU stats
                    cpu_stats = stats.get('cpu_stats', {})
                    precpu_stats = stats.get('precpu_stats', {})
                    cpu_delta = cpu_stats.get('cpu_usage', {}).get('total_usage', 0) - \
                               precpu_stats.get('cpu_usage', {}).get('total_usage', 0)
                    system_delta = cpu_stats.get('system_cpu_usage', 0) - \
                                  precpu_stats.get('system_cpu_usage', 0)
                    num_cpus = cpu_stats.get('online_cpus', 1)
                    if system_delta > 0:
                        cpu_percent = (cpu_delta / system_delta) * num_cpus * 100
            except:
                pass  # Stats not available

        # Get restart count
        restart_count = state.get('RestartCount', 0)

        # Get health status
        health = state.get('Health', {})
        health_status = health.get('Status') if health else None

        return ContainerInfo(
            id=container.short_id,
            name=container.name,
            image=container.image.tags[0] if container.image.tags else container.image.short_id,
            status=container.status,
            state=state.get('Status', 'unknown'),
            ports=ports,
            web_url=web_url,
            labels=container.labels,
            created=created,
            started_at=started_at,
            finished_at=finished_at,
            networks=networks,
            network_mode=network_mode,
            volumes=volumes,
            volume_size_mb=0.0,  # Would need df to calculate
            memory_usage_mb=memory_usage_mb,
            memory_limit_mb=memory_limit_mb,
            memory_percent=memory_percent,
            cpu_percent=cpu_percent,
            restart_count=restart_count,
            health_status=health_status
        )

    def _parse_ports(self, container) -> List[Dict[str, str]]:
        """Parse container port mappings"""
        ports = []
        port_bindings = container.attrs.get('NetworkSettings', {}).get('Ports', {})

        for container_port, host_bindings in port_bindings.items():
            if host_bindings:
                for binding in host_bindings:
                    host_ip = binding.get('HostIp', '0.0.0.0')
                    host_port = binding.get('HostPort', '')

                    # Resolve 0.0.0.0 to actual host IP
                    if host_ip == '0.0.0.0':
                        host_ip = '192.168.12.141'  # arog IP

                    ports.append({
                        'container_port': container_port,
                        'host_ip': host_ip,
                        'host_port': host_port,
                        'url': f"http://{host_ip}:{host_port}" if host_port else None
                    })

        return ports

    def _detect_web_ui(self, container_name: str, ports: List[Dict], labels: Dict) -> Optional[str]:
        """Detect if container has a web UI and return URL"""

        # Priority 1: Check labels for explicit URL
        if 'web.url' in labels:
            return labels['web.url']
        if 'traefik.http.routers' in str(labels):
            # Traefik labeled container
            for key, value in labels.items():
                if 'traefik.http.routers' in key and 'rule' in key.lower():
                    # Extract domain from Traefik rule
                    match = re.search(r'Host\(`([^`]+)`\)', value)
                    if match:
                        return f"http://{match.group(1)}"

        # Priority 2: Match against known patterns
        name_lower = container_name.lower()
        for pattern, default_port in self.WEB_UI_PATTERNS.items():
            if re.search(pattern, name_lower):
                # Find matching port binding
                for port in ports:
                    container_port_num = int(port['container_port'].split('/')[0])
                    if container_port_num == default_port and port['url']:
                        return port['url']

        # Priority 3: Common HTTP ports (80, 443, 8080, 8443, 3000, 5000, etc.)
        http_ports = ['80', '443', '8080', '8443', '3000', '5000', '5001', '9000']
        for port in ports:
            if port['host_port'] in http_ports and port['url']:
                return port['url']

        # Priority 4: If only one port exposed, assume it's the web UI
        if len(ports) == 1 and ports[0]['url']:
            return ports[0]['url']

        return None

    async def restart_container(self, container_id: str) -> Dict:
        """Restart a container"""
        try:
            container = self.client.containers.get(container_id)
            container.restart()
            return {"status": "success", "action": "restart", "container": container_id}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def stop_container(self, container_id: str) -> Dict:
        """Stop a container"""
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            return {"status": "success", "action": "stop", "container": container_id}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def start_container(self, container_id: str) -> Dict:
        """Start a container"""
        try:
            container = self.client.containers.get(container_id)
            container.start()
            return {"status": "success", "action": "start", "container": container_id}
        except Exception as e:
            return {"status": "error", "message": str(e)}
