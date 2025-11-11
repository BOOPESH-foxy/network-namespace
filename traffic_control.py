import subprocess
from typing import Optional

def exec_command_namespace(ns_name: str, cmd: list[str], check: bool = True) -> None:
    full_cmd = ["ip", "netns", "exec", ns_name] + cmd
    subprocess.run(full_cmd, check=check)


def add_delay_loss(
    ns_name: str,ifname: str,
    delay_ms: int = 200,jitter_ms: int = 0,
    loss_percent: float = 0.0):

    cmd = ["tc", "qdisc", "replace", "dev", ifname, "root", "netem"]

    if delay_ms > 0:
        cmd += ["delay", f"{delay_ms}ms"]
        if jitter_ms > 0:
            cmd += [f"{jitter_ms}ms"]

    if loss_percent > 0:
        cmd += ["loss", f"{loss_percent}%"]

    exec_command_namespace(ns_name, cmd)


def clear_qdisc(ns_name: str, ifname: str) -> None:

    cmd = ["tc", "qdisc", "del", "dev", ifname, "root"]
    exec_command_namespace(ns_name, cmd, check=False)
