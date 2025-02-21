import os
import argparse
import subprocess


def generate_keypair():
    private_key = subprocess.check_output("wg genkey", shell=True).decode().strip()
    public_key = (
        subprocess.check_output(f"echo {private_key} | wg pubkey", shell=True)
        .decode()
        .strip()
    )
    return private_key, public_key


def generate_preshared_key():
    return subprocess.check_output("wg genpsk", shell=True).decode().strip()


def write_config(filepath, content):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content)


def generate_server_config(
    num_clients, dns_server, network_interface, server_address, port, network_cidr
):
    server_private_key, server_public_key = generate_keypair()
    server_ip = network_cidr.replace("0/24", "1/24")

    post_up = f"iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o {network_interface} -j MASQUERADE"
    post_down = f"iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o {network_interface} -j MASQUERADE"

    server_config = f"""[Interface]
Address = {server_ip}
ListenPort = {port}
PrivateKey = {server_private_key}
PostUp = {post_up}
PostDown = {post_down}
"""

    clients = []
    for i in range(1, num_clients + 1):
        client_private_key, client_public_key = generate_keypair()
        preshared_key = generate_preshared_key()
        client_ip = network_cidr.replace("0/24", f"{i+1}/32")

        server_config += f"""
[Peer]
PublicKey = {client_public_key}
PresharedKey = {preshared_key}
AllowedIPs = {client_ip}
"""

        clients.append((i, client_private_key, preshared_key, client_ip))

    write_config("./configs/wg-server.conf", server_config)
    return server_private_key, server_public_key, clients


def generate_client_configs(
    clients,
    server_public_key,
    server_address,
    port,
    dns_server,
    full_tunnel,
    network_cidr,
):
    for i, client_private_key, preshared_key, client_ip in clients:
        dns_config = f"DNS = {dns_server}\n" if dns_server else ""
        allowed_ips = "0.0.0.0/0, ::/0" if full_tunnel == "full" else network_cidr

        client_config = f"""[Interface]
Address = {client_ip}
PrivateKey = {client_private_key}
{dns_config}

[Peer]
PublicKey = {server_public_key}
PresharedKey = {preshared_key}
AllowedIPs = {allowed_ips}
Endpoint = {server_address}:{port}
"""

        write_config(f"./configs/wg-client-{i}.conf", client_config)


def main():
    parser = argparse.ArgumentParser(
        description="Generate WireGuard server and client configs."
    )
    parser.add_argument(
        "--num_clients",
        type=int,
        required=True,
        help="Number of client configs to generate",
    )
    parser.add_argument(
        "--dns_server", type=str, required=False, help="DNS server to use (optional)"
    )
    parser.add_argument(
        "--network_interface",
        type=str,
        required=True,
        help="Network interface for iptables",
    )
    parser.add_argument(
        "--server_address", type=str, required=True, help="Server public address"
    )
    parser.add_argument("--port", type=int, required=True, help="WireGuard port")
    parser.add_argument(
        "--network_cidr",
        type=str,
        required=True,
        help="Network CIDR for WireGuard (e.g., 10.0.0.0/24)",
    )
    parser.add_argument(
        "--tunnel",
        type=str,
        choices=["full", "split"],
        default="split",
        help="Specify tunnel mode: 'full' for 0.0.0.0/0, ::/0 or 'split' for VPN subnet only",
    )

    args = parser.parse_args()

    server_private_key, server_public_key, clients = generate_server_config(
        args.num_clients,
        args.dns_server,
        args.network_interface,
        args.server_address,
        args.port,
        args.network_cidr,
    )

    generate_client_configs(
        clients,
        server_public_key,
        args.server_address,
        args.port,
        args.dns_server,
        args.tunnel,
        args.network_cidr,
    )

    print("WireGuard configuration files have been generated in ./configs")


if __name__ == "__main__":
    main()
