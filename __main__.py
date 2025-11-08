import click
from commands.dev import dev
from commands.init import init

@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def main():
    """Your team's unified CLI toolbelt."""
    pass

main.add_command(dev)
main.add_command(init)

if __name__ == "__main__":
    main()
