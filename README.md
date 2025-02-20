# Wireguard configs generator

* Generates a WireGuard server configuration with a NAT rule for forwarding.
* Creates multiple client configurations based on the number specified in the command-line argument.
* Ensures only traffic within 10.0.0.0/24 is routed through the VPN.
* Saves the server config as wg-server.conf and each client config as wg-client-<id>.conf.
* Generates a pre-shared key (PSK) for each client-server pair.

Example usage:
```bash
python generate_wg_configs.py <num_clients> <network_interface> <server_address> <dns_server>

python generate_wg_configs.py 5 enp34s0 example.com 10.0.0.2
```