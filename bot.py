import typing
import os

import discord
from discord.ext import commands
from discord import app_commands
import docker
import psutil

import settings

logger = settings.logging.getLogger("bot")
CONTAINER_NAME = os.getenv("MINECRAFT_CONTAINER")


def run():
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")

        bot.tree.copy_global_to(guild=settings.GUILDS_ID)
        await bot.tree.sync(guild=settings.GUILDS_ID)

    async def command_autocompletion(
        interaction: discord.Interaction, current: str
    ) -> typing.List[app_commands.Choice[str]]:
        data = []
        for mc_command in [
            "clear",
            "day",
            "enable_daylight_cycle",
            "disable_daylight_cycle",
            "help",
            "status",
        ]:
            if current.lower() in mc_command.lower():
                data.append(app_commands.Choice(name=mc_command, value=mc_command))
        return data

    @bot.tree.command()
    @app_commands.autocomplete(mc_command=command_autocompletion)
    async def mc(interaction: discord.Interaction, mc_command: str):
        if mc_command == "help":
            respond_message = """
:star: **Minecraft Server Bot Commands** :star:

`/mc clear`
Clears the weather.

`/mc day`
Sets the time to 'day'.

`/mc enable_daylight_cycle`
Enables the gamerule `doDaylightCycle`.

`/mc disable_daylight_cycle`
Disables the gamerule `doDaylightCycle`.

`/mc status`
Checks if the Minecraft server is running.

:robot: **Additional Information:**
- Make sure the bot has the necessary permissions to interact with the Minecraft server.
- These commands work on the local Minecraft server.

Feel free to reach out if you have any questions or need assistance! Happy crafting! :tools::joystick:
"""

        elif mc_command in (
            "clear",
            "day",
            "enable_daylight_cycle",
            "disable_daylight_cycle",
        ):
            try:
                docker_client = docker.from_env()
                container = docker_client.containers.get(CONTAINER_NAME)
                execute_command = ""
                if mc_command == "clear":
                    execute_command = "weather clear"
                    exec_result = container.exec_run(
                        ["mc-send-to-console", "weather", "clear"]
                    )
                elif mc_command == "day":
                    execute_command = "time set day"
                    exec_result = container.exec_run(
                        ["mc-send-to-console", "time", "set", "day"]
                    )
                elif mc_command in ("enable_daylight_cycle", "disable_daylight_cycle"):
                    daylight_cycle = ""
                    if mc_command == "enable_daylight_cycle":
                        daylight_cycle = "true"
                    elif mc_command == "disable_daylight_cycle":
                        daylight_cycle = "false"
                    execute_command = f"gamerule doDaylightCycle {daylight_cycle}"
                    exec_result = container.exec_run(
                        [
                            "mc-send-to-console",
                            "gamerule",
                            "doDaylightCycle",
                            daylight_cycle,
                        ]
                    )
                output = exec_result.output.decode("utf-8")
                exit_status = exec_result.exit_code

                if exit_status == 0:
                    respond_message = f":white_check_mark: Command `{execute_command}` successfully executed!"
                else:
                    respond_message = f":octagonal_sign: Command `{execute_command}` exited with an error (status code: {exit_status})."

            except docker.errors.NotFound:
                respond_message = (
                    f":question: The container `{CONTAINER_NAME}` does not exist."
                )
            except Exception as e:
                respond_message = f":octagonal_sign: An error occurred: {str(e)}"

        elif mc_command == "status":
            try:
                docker_client = docker.from_env()
                container = docker_client.containers.get(CONTAINER_NAME)
                if container.status == "running":
                    respond_message = (
                        f":up: The container `{CONTAINER_NAME}` is up and running!"
                    )
                else:
                    respond_message = f":octagonal_sign: The container `{CONTAINER_NAME}` is not running."

                respond_message += f"\n\n**CPU usage:** {psutil.cpu_percent(interval=1)} % ; **memory usage:** {psutil.virtual_memory().percent} %\n ; **disk usage:** {psutil.disk_usage('/').percent} %"
            except docker.errors.NotFound:
                respond_message = (
                    f":question: The container `{CONTAINER_NAME}` does not exist."
                )
                respond_message += f"\n\nCPU usage: {psutil.cpu_percent(interval=1)} % || memory usage: {psutil.virtual_memory().percent} % || disk usage: {psutil.disk_usage('/').percent} %"
            except Exception as e:
                respond_message = f":octagonal_sign: An error occurred: {str(e)}"

        await interaction.response.send_message(f"{respond_message}")

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)


if __name__ == "__main__":
    run()
