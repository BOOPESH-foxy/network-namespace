import typer
from net_namespace import NamespaceManager

app = typer.Typer(help="Network namespace simulation")


@app.command("create_namespaces")
def create_namespaces_typer():
    pass

@app.command("create_veth_pair")
def create_veth_pair_typer():
    pass

if __name__ == "__main__":
    app()