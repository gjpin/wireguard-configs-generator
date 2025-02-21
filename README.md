# Wireguard configs generator

* Generates WireGuard server and client configurations automatically.
* Uses wireguard-tools to generate private keys, public keys, and preshared keys.
* Creates a server configuration with NAT and forwarding rules using iptables.
* Creates multiple client configurations based on the specified number of clients.
* Allows specifying a custom network CIDR (e.g., 10.0.0.0/24).
* Supports configuring full tunnel (0.0.0.0/0, ::/0) or split tunnel (VPN subnet only) for clients.
* Optionally includes a DNS server in client configurations.
* Allows setting a custom network interface for NAT rules.
* Saves all configuration files inside the ./configs/ directory.
* Accepts the following command-line arguments:
    --num_clients: Number of client configs to generate.
    --dns_server: (Optional) DNS server to use.
    --network_interface: Network interface for iptables rules.
    --server_address: Public address of the WireGuard server.
    --port: WireGuard listening port.
    --network_cidr: CIDR of the WireGuard network (e.g., 10.0.0.0/24).
    --tunnel: Enables full tunnel mode (0.0.0.0/0, ::/0) or split tunnel (VPN subnet only) for clients. Options are "split" / "full".

Example usage:
```bash
python generate_wg_configs.py \
    --network_cidr 10.0.0.0/24 \
    --num_clients 5 \
    --dns_server 10.0.0.2 \
    --network_interface enp34s0 \
    --server_address example.com \
    --port 51900 \
    --tunnel split
```