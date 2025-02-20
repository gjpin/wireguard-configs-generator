import argparse
import ipaddress
import os
import secrets

def generate_wireguard_configs(num_clients):
    # Define network parameters
    server_ip = ipaddress.ip_address('10.0.0.1')
    subnet = ipaddress.ip_network('10.0.0.0/24')
    server_port = 51820
    dns_peer = ipaddress.ip_address('10.0.0.2')  # Assuming the first client is the DNS peer

    # Create directories for configs
    os.makedirs('wireguard_configs', exist_ok=True)

    # Generate server config
    server_private_key = secrets.token_hex(32)
    server_public_key = secrets.token_hex(32)  # In practice, derive this from the private key
    server_psk = secrets.token_hex(32)

    with open('wireguard_configs/server.conf', 'w') as server_conf:
        server_conf.write(f"[Interface]\n")
        server_conf.write(f"PrivateKey = {server_private_key}\n")
        server_conf.write(f"Address = {server_ip}/24\n")
        server_conf.write(f"ListenPort = {server_port}\n")

        for i in range(1, num_clients + 1):
            client_ip = ipaddress.ip_address(f'10.0.0.{i + 1}')
            client_private_key = secrets.token_hex(32)
            client_public_key = secrets.token_hex(32)  # In practice, derive this from the private key
            client_psk = secrets.token_hex(32)

            server_conf.write(f"\n[Peer]\n")
            server_conf.write(f"PublicKey = {client_public_key}\n")
            server_conf.write(f"AllowedIPs = {client_ip}/32\n")
            server_conf.write(f"PresharedKey = {client_psk}\n")

            # Write client config
            with open(f'wireguard_configs/client{i}.conf', 'w') as client_conf:
                client_conf.write(f"[Interface]\n")
                client_conf.write(f"PrivateKey = {client_private_key}\n")
                client_conf.write(f"Address = {client_ip}/24\n")
                client_conf.write(f"DNS = {dns_peer}\n")

                client_conf.write(f"\n[Peer]\n")
                client_conf.write(f"PublicKey = {server_public_key}\n")
                client_conf.write(f"Endpoint = YOUR_SERVER_IP:{server_port}\n")
                client_conf.write(f"AllowedIPs = {subnet}\n")
                client_conf.write(f"PresharedKey = {client_psk}\n")

                # Add other peers
                for j in range(1, num_clients + 1):
                    if i != j:
                        peer_ip = ipaddress.ip_address(f'10.0.0.{j + 1}')
                        peer_public_key = secrets.token_hex(32)  # In practice, derive this from the private key
                        peer_psk = secrets.token_hex(32)

                        client_conf.write(f"\n[Peer]\n")
                        client_conf.write(f"PublicKey = {peer_public_key}\n")
                        client_conf.write(f"AllowedIPs = {peer_ip}/32\n")
                        client_conf.write(f"PresharedKey = {peer_psk}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate WireGuard configurations.')
    parser.add_argument('num_clients', type=int, help='Number of client configurations to generate')
    args = parser.parse_args()

    generate_wireguard_configs(args.num_clients)
