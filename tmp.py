from rich.spinner import Spinner
from rich.console import Console
from time import sleep
from rich.live import Live

console = Console()

spinner = Spinner("aesthetic")
with Live(
    Spinner("aesthetic"),
    transient = True,
    refresh_per_second = 20,
    ) as live:
        sleep(1)

console.clear_live()
