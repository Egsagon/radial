'''
    Radial
'''

import json5
import asyncio
import discord
import python_aternos as at

ps1 = '\033[95m🛆\033[0m'

class Bot(discord.Client):
    
    def __init__(self) -> None:
        '''
        Represents an instance of the bot.
        '''
        
        # Initial setup
        self.server: at.AternosServer = None
        self.conf: dict = json5.load(open('config.jsonc'))        
        self.client = at.Client.from_credentials(**self.conf['aternos'])
        
        # Initialise bot
        super().__init__(intents = discord.Intents.all())
    
    async def setup(self, servid: str) -> None:
        '''
        Setup a connection for a new server.
        '''
        
        # Update the server object
        self.server = self.client.get_server(servid)
        
        # Build the handler wrapper
        socket = self.server.wss()
        
        @socket.wssreceiver(at.atwss.Streams.status)
        async def status(data: dict) -> None:
            
            act = self.make_activity(data)
            
            print(ps1, f'Changing presence to {act}')
            
            await self.change_presence(activity = discord.Game(act))
        
        # Connect to the socket
        asyncio.get_event_loop().create_task(socket.connect())
        print(ps1, f'[SETUP] Created new connection to \033[92m{servid}`\033[0m')
    
    async def on_ready(self) -> None:
        '''
        Handle bot starting.
        '''
        
        print(ps1, 'Bot started')
        
        if servid := self.conf['server_id']: await self.setup(servid)
    
    async def on_message(self, msg: discord.Message) -> None:
        '''
        Handle commands execution.
        '''
        
        if not msg.content.startswith('?rad'): return
        command = msg.content.split()[1:]
        
        match command:
            
            case ['start' | 'stop' | 'restart' | 'cancel' | 'confirm' as cmd, *args]:
                '''
                Execute a server function.
                '''
                
                if self.server is None: return await msg.reply('Please select a server first.')
                
                # Call method
                try:
                    m = f'{cmd.capitalize()}ing server'
                    await msg.reply(f'{m}ing server')
                    print(ps1, m)
                    
                    eval(f'cur.{cmd}')()
                    
                # Send errors if any
                except Exception as e:
                    print(e.args)
                    await msg.reply(f'Failed to call method: ```md\n{e.args}```')
            
            case ['set', *args]:
                '''
                Define the current server.
                '''
                
                # Display all available servers
                if not len(args):
                    servers = [serv.domain for serv in self.client.list_servers(False)]
                    rep = '\n'.join(map(lambda l: f'{l[0]: <2} - {l[1]}', enumerate(servers)))
                    _cr = 'none' if self.server is None else self.server.domain
                    
                    return await msg.reply(f'Current server: `{_cr}`\nAvailable servers: ```json\n{rep}```')
                
                # Setup a particula server
                index = int(args[0])
                servers = self.client.list_servers(False)
                
                # Index error protection
                if not 0 <= index <= (lenght := len(servers)) - 1:
                    await msg.reply(f'Invalid server index (must be from 0 to {lenght})')
                
                # Switch server
                self.server = servers[index]
                self.conf['server_id'] = self.server.servid
                
                # connect to the socket
                await self.setup(self.server.servid)
                
                # Debug
                m = f'Changed server to `{self.server.servid}`'
                print(ps1, m)
                await msg.reply(m)
    
            case unhandled:
                '''
                Error handling
                '''
            
                await msg.reply(f'Unhandled or invalid syntax: `{" -> ".join(unhandled)}`.')
    
    def run(self) -> None:
        '''
        Wraps discord.Client.run to run the bot.
        '''
        
        try: super().run(self.conf['token'])
    
        # Save config
        except KeyboardInterrupt:
            open('config.jsonc', 'w').write(json5.dumps(self.conf, indent = 3))
    
    def make_activity(self, data: dict) -> str:
        '''
        Parse a data dict to an activity string.
        '''
        
        status = data['lang']
        players = data['players']
        
        online = status == 'online'
        return f"{status.upper()} {f'(#{players})' if online else ''}"


if __name__ == '__main__': Bot().run()

# EOF