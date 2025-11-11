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

## Usage

From the repo root:

```bash
cd /path/to/network-namespace
```

### 1. Create Two Namespaces Only

```bash
sudo python3 main.py create_namespaces sva svb
```

This will:

- create namespaces `sva` and `svb` (if they don’t already exist)

Check them:

```bash
ip netns list
```

You should see:

```text
sva
svb
```

---

### 2. Create a Veth Pair Between Two Namespaces

```bash
sudo python3 main.py create_veth_pair sva svb
```

This will:

- ensure `sva` and `svb` namespaces exist
- create a veth pair: `veth-a` ↔ `veth-b`
- move:
  - `veth-a` into `sva`
  - `veth-b` into `svb`
- assign IPs from `10.10.0.0/30`:
  - `sva: 10.10.0.1`
  - `svb: 10.10.0.2`
- bring interfaces up and add simple routes

You can inspect:

```bash
sudo ip netns exec sva ip addr
sudo ip netns exec svb ip addr
```

---

### 3. Test Connectivity

From `svb` ping `sva`:

```bash
sudo ip netns exec svb ping 10.10.0.1
```

You should see `ping` replies as if they were two separate machines on a tiny /30 network.

You can also open shells inside each namespace:

```bash
sudo ip netns exec sva bash
sudo ip netns exec svb bash
```

Then run whatever apps you like inside those isolated network worlds.

---

## Cleanup

The `NamespaceManager` is written to be reasonably idempotent (it tries to clean up conflicting veths), but you may still want to manually clean up when you’re done.

```bash
# Delete namespaces
sudo ip netns del sva 2>/dev/null
sudo ip netns del svb 2>/dev/null

# Delete any leftover veths in root namespace
sudo ip link del veth-a 2>/dev/null
sudo ip link del veth-b 2>/dev/null
```

Check again:

```bash
ip netns list
ip link show | grep veth
```

---

## Internals (Short Version)

- `NamespaceManager.create_namespace(name)`
  - wraps `ip netns add` using `pyroute2`

- `NamespaceManager.create_veth_pair(ns_a, ns_b, if_a, if_b, cidr)`
  - deletes any old `if_a` / `if_b` interfaces across all namespaces
  - creates a veth pair in the root namespace
  - moves `if_a` into `ns_a` and `if_b` into `ns_b`
  - allocates two IPs from `cidr` (by default `10.10.0.1` and `10.10.0.2`)
  - assigns IPs and brings interfaces up
  - adds simple routes (ignores “File exists” netlink errors so reruns are safe)

---

## Roadmap / Future Ideas

This repo currently focuses on **netns + veth setup**. Planned ideas:

- Add `tc netem` helpers to simulate:
  - delay
  - packet loss
  - bandwidth limits
- Add CLI commands:
  - `add-delay`, `clear-qdisc`, etc.
- Add YAML-based scenario definitions
- Add a small REST API to trigger experiments remotely
- Integrate with chaos tools / CI pipelines

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'typer'` (or `pyroute2`)

Make sure it’s installed for the same Python you use with `sudo`:

```bash
sudo python3 -m pip install typer pyroute2
```

### `NetlinkError: (17, 'File exists')`

This usually means an interface / IP / route already exists.

The code already tries to handle this, but if you see it:

1. Clean up manually:
   ```bash
   sudo ip netns del sva svb 2>/dev/null
   sudo ip link del veth-a veth-b 2>/dev/null
   ```
2. Re-run `create_veth_pair`.

---

