import os
import sys
import subprocess


def generate_keypair():
    private_key = subprocess.check_output("wg genkey", shell=True).decode().strip()
    public_key = (
        subprocess.check_output(f"echo {private_key} | wg pubkey", shell=True)
        .decode()
        .strip()
    )
    return private_key, public_key


def generate_psk():
    return subprocess.check_output("wg genpsk", shell=True).decode().strip()


def generate_server_config(
    num_clients, network_interface, server_address, dns_server, listen_port=51820
):
    os.makedirs("configs", exist_ok=True)
    server_private_key, server_public_key = generate_keypair()
    server_config = f"""[Interface]
Address = 10.0.0.1/24
ListenPort = {listen_port}
PrivateKey = {server_private_key}
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o {network_interface} -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o {network_interface} -j MASQUERADE
"""
    clients = []
    for i in range(2, num_clients + 2):
        client_private_key, client_public_key = generate_keypair()
        psk = generate_psk()
        clients.append((i, client_private_key, client_public_key, psk))
        server_config += f"""
[Peer]
PublicKey = {client_public_key}
PresharedKey = {psk}
AllowedIPs = 10.0.0.{i}/32
"""

    with open("configs/wg-server.conf", "w") as f:
        f.write(server_config)

    print("Server configuration written to configs/wg-server.conf")
    return server_public_key, clients


def generate_client_config(
    client_id,
    client_private_key,
    server_public_key,
    psk,
    server_address,
    dns_server,
    listen_port=51820,
):
    client_config = f"""[Interface]
Address = 10.0.0.{client_id}/24
ListenPort = {listen_port}
PrivateKey = {client_private_key}
DNS = {dns_server}

[Peer]
PublicKey = {server_public_key}
PresharedKey = {psk}
AllowedIPs = 10.0.0.0/24
Endpoint = {server_address}:{listen_port}
"""
    filename = f"configs/wg-client-{client_id}.conf"
    with open(filename, "w") as f:
        f.write(client_config)
    print(f"Client configuration written to {filename}")


def main():
    if len(sys.argv) != 5:
        print(
            "Usage: python generate_wg_configs.py <num_clients> <network_interface> <server_address> <dns_server>"
        )
        sys.exit(1)

    num_clients = int(sys.argv[1])
    network_interface = sys.argv[2]
    server_address = sys.argv[3]
    dns_server = sys.argv[4]
    server_public_key, clients = generate_server_config(
        num_clients, network_interface, server_address, dns_server
    )

    for client_id, client_private_key, _, psk in clients:
        generate_client_config(
            client_id,
            client_private_key,
            server_public_key,
            psk,
            server_address,
            dns_server,
        )


if __name__ == "__main__":
    main()
