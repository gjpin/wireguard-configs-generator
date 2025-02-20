import argparse
import ipaddress
import os
import subprocess
import base64
import secrets


def generate_wireguard_key():
    # Generate a private key using wg
    private_key = subprocess.check_output(["wg", "genkey"]).decode().strip()
    # Generate the corresponding public key
    public_key = (
        subprocess.check_output(["wg", "pubkey"], input=private_key.encode())
        .decode()
        .strip()
    )
    return private_key, public_key


def generate_psk():
    # Generate a 32-byte random sequence
    psk_bytes = secrets.token_bytes(32)
    # Encode the bytes in base64
    psk = base64.b64encode(psk_bytes).decode("utf-8")
    return psk


def generate_wireguard_configs(num_clients):
    # Define network parameters
    server_ip = ipaddress.ip_address("10.0.0.1")
    subnet = ipaddress.ip_network("10.0.0.0/24")
    server_port = 51820
    dns_peer = ipaddress.ip_address(
        "10.0.0.2"
    )  # Assuming the first client is the DNS peer

    # Create directories for configs
    os.makedirs("wireguard_configs", exist_ok=True)

    # Generate server keys
    server_private_key, server_public_key = generate_wireguard_key()

    with open("wireguard_configs/server.conf", "w") as server_conf:
        server_conf.write(f"[Interface]\n")
        server_conf.write(f"PrivateKey = {server_private_key}\n")
        server_conf.write(f"Address = {server_ip}/24\n")
        server_conf.write(f"ListenPort = {server_port}\n")

        for i in range(1, num_clients + 1):
            client_ip = ipaddress.ip_address(f"10.0.0.{i + 1}")
            client_private_key, client_public_key = generate_wireguard_key()
            client_psk = generate_psk()

            server_conf.write(f"\n[Peer]\n")
            server_conf.write(f"PublicKey = {client_public_key}\n")
            server_conf.write(f"AllowedIPs = {client_ip}/32\n")
            server_conf.write(f"PresharedKey = {client_psk}\n")

            # Write client config
            with open(f"wireguard_configs/client{i}.conf", "w") as client_conf:
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
                        peer_ip = ipaddress.ip_address(f"10.0.0.{j + 1}")
                        peer_public_key = generate_wireguard_key()[1]
                        peer_psk = generate_psk()

                        client_conf.write(f"\n[Peer]\n")
                        client_conf.write(f"PublicKey = {peer_public_key}\n")
                        client_conf.write(f"AllowedIPs = {peer_ip}/32\n")
                        client_conf.write(f"PresharedKey = {peer_psk}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate WireGuard configurations.")
    parser.add_argument(
        "num_clients", type=int, help="Number of client configurations to generate"
    )
    args = parser.parse_args()

    generate_wireguard_configs(args.num_clients)
