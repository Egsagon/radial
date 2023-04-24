# radial
Radial - Discord bot that start or stop aternos servers.

This bot provide the ability for all the members of a discord server to automatically start and stop a minecraft aternos server.

> :warning: This bot uses an unofficial [Aternos api](https://github.com/DarkCat09/python-aternos), which it against Aternos TOS.

License: Apache 2.0 - see the `LICENSE` file.

## Setup
Required dependencies: `discord`, `python_aternos`.

To run the bot, you must use an aternos account. It can be a server owner account, but preferably an empty account that have access
to the minimum permission.

You must enter the account credentials, along with the discord bot token in the `config.jsonc` file.
The discord bot need all intents.

## Usage
The following commands are available:
```jsonc
?rad start        // Start the current server
?rad restart      // Restart the current server
?rad cancel       // Cancel the start of the current server
?rad confirm      // In case the server is in queue, confirm the start of the server

?rad set <index>  // Select the current server by index.
                  // If no index is provided, return the indexes of each server.
```

The bot will display as an activity the status of the server (starting, stopping, online, etc.)
along with some useful information (player count, queue time, etc.).

## Note on status update
One intended feature of this bot was to display the server status as the bot presence ('starting', 'stopping', etc.) with the amount
of players on the server, to let people know if they could join people to play with. Unfortunatly, Aternos seem to detect that,
whichever method we use for that (server fetch, server wssconnect or the mcstatus module). Therefore, this feature has been removed
as of now.