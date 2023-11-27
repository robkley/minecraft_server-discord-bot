# Minecraft Server Discord Bot

## Overview
The Discord Minecraft Server Bot is a Python-based Discord bot designed to enhance the management and interaction with a local Minecraft server. The bot provides convenient commands to control specific aspects of the Minecraft server directly from your Discord server.

## Usage
1. Clone this project to your server where you want the Discord Minecraft Server Bot to run.
2. Set the following environment variables:
   - **DISCORD_TOKEN**: Your Discord bot token. Obtain this by creating a bot on the Discord Developer Portal.
   - **GUILD_ID**: The ID of the Discord server (guild) where you want the bot to operate.
   - **MINECRAFT_CONTAINER**: The name of the Docker container with your Minecraft server.
3. Grant the bot the necessary permissions to interact with the Minecraft server.
4. Run the bot script to start the Discord Minecraft Server Bot.
5. Start using the provided commands in your Discord server:
    - `!mc clear` - Clears the weather on the local Minecraft server.
    - `!mc day` - Sets the time to 'day' on the local Minecraft server.
    - `!mc status`: Checks if the Minecraft server is running.

## Additional Information
- Ensure the bot has the required permissions to communicate with the Minecraft server.
- These commands are tailored for a local Minecraft server environment.

Feel free to explore the capabilities of the Discord Minecraft Server Bot and reach out if you have any questions or need assistance. Happy crafting! 🛠️🎮