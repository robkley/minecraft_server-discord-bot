from datetime import datetime
from time import sleep
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
            "creative",
            "survival",
            "help",
            "status",
            "resources",
        ]:
            if current.lower() in mc_command.lower():
                data.append(app_commands.Choice(name=mc_command, value=mc_command))
        return data

    @bot.tree.command()
    @app_commands.autocomplete(discord_command_option=command_autocompletion)
    async def mc(interaction: discord.Interaction, discord_command_option: str):
        if discord_command_option == "help":
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

`/mc creative`
Sets gamemode of user using the command to `creative`.

`/mc survival`
Sets gamemode of user using the command to `survival`.

`/mc status`
Checks if the Minecraft server is running and prints out resource information.

`/mc resources`
Prints out resource information for the server host system for 20 seconds every 2 seconds.

:robot: **Additional Information:**
- Make sure the bot has the necessary permissions to interact with the Minecraft server.
- These commands work on the local Minecraft server.

Feel free to reach out if you have any questions or need assistance! Happy crafting! :tools::joystick:
"""

        elif discord_command_option in (
            "clear",
            "day",
            "enable_daylight_cycle",
            "disable_daylight_cycle",
            "creative",
            "survival",
            "resources",
        ):
            try:
                docker_client = docker.from_env()
                container = docker_client.containers.get(CONTAINER_NAME)
                execute_command = True
                mc_command = ""
                if discord_command_option == "clear":
                    mc_command = f"weather {discord_command_option}"
                    command_args = [
                        "mc-send-to-console",
                        "weather",
                        discord_command_option,
                    ]

                elif discord_command_option == "day":
                    mc_command = f"time set {discord_command_option}"
                    command_args = [
                        "mc-send-to-console",
                        "time",
                        "set",
                        discord_command_option,
                    ]
                elif discord_command_option in (
                    "enable_daylight_cycle",
                    "disable_daylight_cycle",
                ):
                    daylight_cycle = ""
                    if discord_command_option == "enable_daylight_cycle":
                        daylight_cycle = "true"
                    elif discord_command_option == "disable_daylight_cycle":
                        daylight_cycle = "false"
                    mc_command = f"gamerule doDaylightCycle {daylight_cycle}"
                    command_args = [
                        "mc-send-to-console",
                        "gamerule",
                        "doDaylightCycle",
                        daylight_cycle,
                    ]
                elif discord_command_option in ("creative", "survival"):
                    match interaction.message.author.name:
                        case "discord_user":
                            mc_user = "mc_user."
                        case _:
                            mc_user = ""
                    if mc_user == "":
                        respond_message = f":octagonal_sign: Couldn't map Discord user `{interaction.message.author.name}` to a Minecraft player."
                        execute_command = False
                    mc_command = f"gamemode {discord_command_option} {mc_user}"
                    command_args = [
                        "mc-send-to-console",
                        "gamemode",
                        discord_command_option,
                        mc_user,
                    ]

                if execute_command:
                    exec_result = container.exec_run(command_args)
                    output = exec_result.output.decode("utf-8")
                    exit_status = exec_result.exit_code

                    if exit_status == 0:
                        respond_message = f":white_check_mark: Command `{mc_command}` successfully executed!"
                    else:
                        respond_message = f":octagonal_sign: Command `{mc_command}` exited with an error (status code: {exit_status})."

            except docker.errors.NotFound:
                respond_message = (
                    f":question: The container `{CONTAINER_NAME}` does not exist."
                )
            except Exception as e:
                respond_message = f":octagonal_sign: An error occurred: {str(e)}"

        elif discord_command_option == "status":
            try:
                docker_client = docker.from_env()
                container = docker_client.containers.get(CONTAINER_NAME)
                if container.status == "running":
                    respond_message = (
                        f":up: The container `{CONTAINER_NAME}` is up and running!"
                    )
                else:
                    respond_message = f":octagonal_sign: The container `{CONTAINER_NAME}` is not running."

                respond_message += {
                    "\n```yaml\n"
                    f"CPU usage:    {psutil.cpu_percent(interval=1)} %\n"
                    f"Memory usage: {psutil.virtual_memory().percent}%\n"
                    f"Disk usage:   {psutil.disk_usage('/').percent}%\n"
                    "```"
                }
            except docker.errors.NotFound:
                respond_message = (
                    f":question: The container `{CONTAINER_NAME}` does not exist."
                )
                respond_message += {
                    "\n```yaml\n"
                    f"CPU usage:    {psutil.cpu_percent(interval=1)} %\n"
                    f"Memory usage: {psutil.virtual_memory().percent}%\n"
                    f"Disk usage:   {psutil.disk_usage('/').percent}%\n"
                    "```"
                }
            except Exception as e:
                respond_message = f":octagonal_sign: An error occurred: {str(e)}"

        elif discord_command_option == "resources":
            for i in range(0, 10):
                try:
                    respond_message = {
                        f":information_source: Check after {i * 2} seconds ({datetime.now().strftime('%d.%m.%Y %H:%M:%S')})\n"
                        "```yaml\n"
                        f"CPU usage:    {psutil.cpu_percent(interval=1)} %\n"
                        f"Memory usage: {psutil.virtual_memory().percent}%\n"
                        f"Disk usage:   {psutil.disk_usage('/').percent}%\n"
                        "```"
                    }
                except Exception as e:
                    respond_message = f":octagonal_sign: An error occurred: {str(e)}"
                await interaction.response.send_message(f"{respond_message}")
                sleep(2)

        if discord_command_option != "resources":
            await interaction.response.send_message(f"{respond_message}")

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)


if __name__ == "__main__":
    run()
