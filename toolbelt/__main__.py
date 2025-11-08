import click
from toolbelt.commands.dev import dev
from toolbelt.commands.init import init


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def main():
    """Your team's unified CLI toolbelt."""
    pass


main.add_command(dev)
main.add_command(init)

if __name__ == "__main__":
    main()
