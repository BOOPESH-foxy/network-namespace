# chaos/netns.py
from pyroute2 import IPRoute, NetNS, netns
from ipaddress import IPv4Network

class NamespaceManager:
    def __init__(self):
        self.ipr = IPRoute()

    def create_namespace(self, name: str):
        if name not in netns.listnetns():
            netns.create(name)

    def delete_namespace(self, name: str):
        if name in netns.listnetns():
            netns.remove(name)

    def create_veth_pair(self,
        ns_a: str,ns_b: str,
        if_a: str = "veth-a",if_b: str = "veth-b",
        cidr: str = "10.10.0.0/30",
    ):

        self.create_namespace(ns_a)
        self.create_namespace(ns_b)

        self.ipr.link("add", ifname=if_a, peer=if_b, kind="veth")

        idx_a = self.ipr.link_lookup(ifname=if_a)[0]
        idx_b = self.ipr.link_lookup(ifname=if_b)[0]

        self.ipr.link("set", index=idx_a, net_ns_fd=ns_a)
        self.ipr.link("set", index=idx_b, net_ns_fd=ns_b)

        net = IPv4Network(cidr)
        ip_a = str(list(net.hosts())[0])  # usually .1
        ip_b = str(list(net.hosts())[1])  # usually .2

        with NetNS(ns_a) as ns:
            idx_a_ns = ns.link_lookup(ifname=if_a)[0]
            ns.addr(
                "add",
                index=idx_a_ns,
                address=ip_a,
                prefixlen=net.prefixlen,
            )
            ns.link("set", index=idx_a_ns, state="up")
            ns.route("add", dst=str(net), gateway=ip_a)

        with NetNS(ns_b) as ns:
            idx_b_ns = ns.link_lookup(ifname=if_b)[0]
            ns.addr(
                "add",
                index=idx_b_ns,
                address=ip_b,
                prefixlen=net.prefixlen,
            )
            ns.link("set", index=idx_b_ns, state="up")
            ns.route("add", dst=str(net), gateway=ip_b)

        return {
            "ns_a": ns_a,
            "ns_b": ns_b,
            "if_a": if_a,
            "if_b": if_b,
            "ip_a": ip_a,
            "ip_b": ip_b,
            "cidr": cidr,
        }
