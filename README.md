# Network Namespace Simulator

A tiny Python tool to **create Linux network namespaces** and **connect them with veth pairs** for network simulation and (later) chaos engineering.

Right now it focuses on:

- Creating isolated network namespaces
- Connecting two namespaces with a virtual Ethernet (veth) link
- Assigning IPs so you can ping between them and run services inside

>  **Linux only** – this project relies on `ip netns`, `veth`, and `tc` (later), so it needs a Linux kernel and `iproute2`.

---

## Why?

When you develop or test distributed systems, everything usually runs on:

- the same machine
- on `localhost`
- with nearly perfect network conditions

Real networks are not like that.

Network namespaces let you:

- emulate **separate machines** on one host
- isolate processes into their own "network universe"
- connect them with virtual links you can later slow down, drop packets on, etc.

This project gives you a **simple CLI** to spin up those namespaces + links quickly, so you can start experimenting.

---

## Project Layout

Example repo structure:

```text
.
├── main.py           # Typer CLI entrypoint
├── net_namespace.py  # NamespaceManager: netns + veth logic
└── README.md
```

- `net_namespace.py` defines `NamespaceManager`
- `main.py` exposes a CLI using [Typer](https://typer.tiangolo.com/)

---

## Requirements

- Python 3.8+
- Linux with `iproute2` installed (`ip`, `ip netns`, `tc`, etc.)
- Python dependencies:
  - `typer`
  - `pyroute2`

Install system packages (Ubuntu / Debian):

```bash
sudo apt-get update
sudo apt-get install -y iproute2
```

Install Python deps:

```bash
python3 -m pip install typer pyroute2
```

If you are using `sudo` to run the script, you may also need:

```bash
sudo python3 -m pip install typer pyroute2
```

> Note: network operations require `CAP_NET_ADMIN`, so most commands below are shown with `sudo`.

---

