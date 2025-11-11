import typer
from net_namespace import NamespaceManager

app = typer.Typer(help="Network namespace simulation")

@app.command("create_namespaces")
def create_namespaces_typer(
    ns_a: str = typer.Argument("svc-a", help="Name of the first namespace"),
    ns_b: str = typer.Argument("svc-b", help="Name of the second namespace")):

    ns_manager = NamespaceManager()
    ns_manager.create_namespace(ns_a)
    ns_manager.create_namespace(ns_b)

    typer.echo(f"Created (or already existed): {ns_a}, {ns_b}")


@app.command("create_veth_pair")
def create_veth_pair_typer(
    ns_a: str = typer.Argument("svc-a", help="First namespace name"),
    ns_b: str = typer.Argument("svc-b", help="Second namespace name"),
    if_a: str = typer.Option("veth-a", "--if-a", help="Interface name in ns_a"),
    if_b: str = typer.Option("veth-b", "--if-b", help="Interface name in ns_b"),
    cidr: str = typer.Option(
        "10.10.0.0/30",
        "--cidr",
        help="CIDR for the point-to-point link between namespaces",
    ),
):
    """
    Create two namespaces (if needed) and connect them with a veth pair.
    """
    ns_manager = NamespaceManager()
    info = ns_manager.create_veth_pair(
        ns_a=ns_a,
        ns_b=ns_b,
        if_a=if_a,
        if_b=if_b,
        cidr=cidr,
    )

    typer.echo("Veth pair created and configured:")


if __name__ == "__main__":
    app()
