"""Local development launcher for the RL IDE backend gateway."""

from __future__ import annotations

import os
import socket

import uvicorn
from zeroconf import ServiceInfo, Zeroconf

from backend.settings import RuntimeSettings


def _discover_local_ips() -> list[str]:
    """Return IPv4 addresses that can be useful for device-based demos."""
    interfaces = socket.getaddrinfo(socket.gethostname(), None)
    ips: set[str] = set()
    for item in interfaces:
        ip = item[4][0]
        if ":" not in ip and ip != "127.0.0.1":
            ips.add(ip)
    return sorted(ips)


def _print_startup_addresses(port: int) -> str:
    print("\n" + "=" * 50)
    print("RL IDE BACKEND STARTUP")
    print("=" * 50)
    print("For iPad or physical device demos, use one of these URLs:")
    try:
        hostname = socket.gethostname()
        ips = _discover_local_ips()
        print(f" - Hostname: http://{hostname}.local:{port}")
        for ip in ips:
            print(f" - Local IP: http://{ip}:{port}")
        return ips[0] if ips else "127.0.0.1"
    except Exception:
        print(" - Could not auto-detect local IPs. Check System Settings > Network.")
        return "127.0.0.1"
    finally:
        print("=" * 50 + "\n")


def _build_mdns_service(best_ip: str, port: int) -> ServiceInfo:
    return ServiceInfo(
        "_rl-ide._tcp.local.",
        "RL IDE Backend._rl-ide._tcp.local.",
        addresses=[socket.inet_aton(best_ip)],
        port=port,
        properties={"desc": "RL Backend"},
        server="rl-ide.local.",
    )


if __name__ == "__main__":
    settings = RuntimeSettings.from_env()
    best_ip = _print_startup_addresses(settings.gateway_port)

    mdns = Zeroconf()
    service_info = _build_mdns_service(best_ip, settings.gateway_port)
    mdns.register_service(service_info)

    try:
        uvicorn.run(
            "backend.api_gateway.base:create_app",
            host=os.getenv("RL_IDE_BACKEND_HOST", "0.0.0.0"),
            port=settings.gateway_port,
            reload=settings.backend_reload,
            factory=True,
        )
    finally:
        mdns.unregister_service(service_info)
        mdns.close()
