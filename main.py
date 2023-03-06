'''
    Radial
'''

import os
import json
import time
import random
import discord
import logging
import get_status
from discord.ext import tasks
from datetime import timedelta
import python_aternos as aternos

# Clear shell
os.system('clear')

# Settings
ps1 = '\033[96m🛆\033[0m'
creds = json.load(open('creds.json'))
config = json.load(open('data.json'))
fetcher = get_status.Fetcher.using_mcstatus
formater = logging.Formatter(ps1 + '\033[91m Error at %(asctime)s: %(message)s', datefmt = '%d/%m %H:%M')

# Setup clients
bot = discord.Client(intents = discord.Intents.all())
api = aternos.Client.from_credentials(creds['usr'], creds['pwd'])

# Load server
cur = None
if config['id']:
    cur = api.get_server(config['id'])
    print(ps1, f'Resumed last session server: {config["id"]}')

def inject() -> None:
    '''
    Inject misc methods into the current server.
    Least productive refactoring decision ever taken.
    '''
    
    if cur is not None:
        # Head method: start server bypassing EULA and queue
        cur.head = lambda *_: cur.start(True, True)
        
        ...

inject()

@bot.event
async def on_ready() -> None:
    # Start the bot
    
    print(ps1, 'Bot ready')
    status_looper.start()

async def throw(error: Exception, msg: discord.Message) -> None:
    # Handle displaying an error
    
    print(ps1, f'ERR: {type(error)} -> {error.args}')
    await msg.reply(f'Failed to call method: ` {type(error)} ` raised: ```{repr(error)}```')

@bot.event
async def on_message(msg: discord.Message) -> None:
    # Receive messages
    
    global cur
    
    # Parse args
    if not msg.content.startswith('?radial'): return
    args = msg.content.split()[1:]
    
    match args:
        
        case ['start' | 'stop' |'restart' | 'cancel' | 'confirm' | 'head' as action, *_]:
            # Call a server action
            
            # No server error protection
            if cur is None: return await msg.reply('Please select a server first.')
            
            print(ps1, f'{action}ing server `{cur.domain}`')
            
            # Call method
            try:
                eval(f'cur.{action}')()
                await msg.reply(f'{action.capitalize()}ing server')
            
            # Send errors if any
            except Exception as err: await throw(err, msg)
        
        case ['tick', *params]:
            # Change ticking interval
            
            if not len(params):
                # Display tick
                
                await msg.reply(f'Current tick frequency: `{config["re"]}s`.')
            
            else:
                tick = float(params[0])
                
                # Save data
                config['re'] = tick
                open('data.json', 'w').write(json.dumps(config, indent = 3))
                status_looper.change_interval(seconds = config['re'])
                
                # Debug
                print(ps1, f'Changed tick frequency to {tick}s.')
                await msg.reply(f'Changed tick frequency to `{config["re"]}s`.')
        
        case ['select', *params]:
            # Select server
            
            if not len(params):
                # Display servers
                
                servers = [serv.domain for serv in api.list_servers(False)]
                rep = '\n'.join(map(lambda l: f'{l[0]: <2} - {l[1]}', enumerate(servers)))
                _cr = 'none' if cur is None else cur.domain
                
                await msg.reply(f'Current server: `{_cr}`\nAvailable servers: ```json\n{rep}```')
            
            else:
                # Switch to server
                
                index = int(params[0])
                servers = api.list_servers(False)
                
                if not 0 <= index <= len(servers) - 1:
                    await msg.reply(f'Invalid server index (must be from 0 to {len(servers)})')
                
                # Switch server
                cur = servers[index]
                config['id'] = cur.servid
                
                # Save to config
                open('data.json', 'w').write(json.dumps(config, indent = 3))
                
                # Debug
                print(ps1, f'Changed server to `{cur.servid}`')
                await msg.reply(f'Switched to server `{cur.domain}`.')
                
                # Inject server misc actions
                inject()
        
        case ['info', *params]:
            # Display current server infos
            
            if cur is None: return await msg.reply('Please select a server first.')
            
            cur.fetch()
            data = cur._info
            
            print(ps1, f'Sending data for {msg.author}')
            await msg.reply(f'Fetched data: ```json\n{json.dumps(data, indent = 3)}```')
        
        case unhandled:
            # Error handling
            
            await msg.reply(f'Unhandled or invalid syntax: `{" -> ".join(unhandled)}`.')

@tasks.loop(seconds = config['re'])
async def status_looper() -> None:
    # Constantly update bot status
    
    # No server error protection
    if cur is None:
        return print(ps1, 'Tried to update presence, but no current server.')
    
    print(ps1, 'Updating presence')
    
    # Fetch data
    try:
        data = fetcher(cur.domain)
        await bot.change_presence(activity = discord.Game(get_status.format(*data)))
    
    except Exception as e:
        print(ps1, f'\033[91mFetching error: {e.args}\033[0m')

bot.run(creds['tkn'], log_level = logging.ERROR, log_formatter = formater)

# EOF