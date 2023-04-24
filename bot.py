'''
    Radial
'''

import json
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
        self.conf: dict = json.load(open('config.json'))
        self.client = at.Client.from_credentials(**self.conf['aternos'])
        
        # Initialise bot
        super().__init__(intents = discord.Intents.all())
    
    async def on_ready(self) -> None:
        '''
        Handle bot starting.
        '''
        
        print(ps1, 'Bot started')
        
        # Load using saved address
        if addr := self.conf['current']:
            self.server = self.client.get_server(addr)
    
    async def on_message(self, msg: discord.Message) -> None:
        '''
        Handle commands execution.
        '''
        
        if not msg.content.startswith('?rad'): return
        command = msg.content.lower().split()[1:]
        
        match command:
            
            case ['start' | 'stop' | 'restart' | 'cancel' | 'confirm' as cmd, *args]:
                '''
                Execute a server function.
                '''
                
                if self.server is None: return await msg.reply('Please select a server first.')
                
                # Call method
                try:
                    m = f'{cmd.capitalize()}ing server'
                    await msg.reply('> ' + m)
                    print(ps1, m)
                    
                    eval(f'self.server.{cmd}')()
                    
                    # presence = cmd.upper() if not cmd in ['start', 'head'] else 'ONLINE'
                    # await self.change_presence(activity = discord.Game(presence))
                    
                # Send errors if any
                except Exception as e:
                    print(e.args)
                    await msg.reply(f'> Internal error: ```md\n{e.args}```')
            
            case ['set', *args]:
                '''
                Define the current server.
                '''
                
                servers = self.client.list_servers()
                
                # Display all available servers
                if not len(args):
                    domains = [serv.domain for serv in servers]
                    rep = '\n'.join(map(lambda l: f'{l[0]: <2} - {l[1]}', enumerate(domains)))
                    _cr = 'none' if self.server is None else self.server.domain
                    
                    return await msg.reply(f'> Current server: `{_cr}`\nAvailable servers: ```json\n{rep}```')
                
                # Setup a particula server
                index = int(args[0])
                
                # Index error protection
                if not 0 <= index <= (lenght := len(servers)) - 1:
                    await msg.reply(f'> Invalid server index (must be from 0 to {lenght})')
                
                # Switch server
                self.server = servers[index]
                self.conf['current'] = self.server.servid
                
                # Save to config
                with open('config.json', 'w') as f:
                    f.write(json.dumps(self.conf, indent = 3))
                
                # Debug
                m = f'> Changed server to `{self.server.domain}`'
                print(ps1, m)
                await msg.reply(m)
    
            case []:
                # Show server data
                
                if self.server is None:
                    return await msg.reply('> No server selected.')
                
                self.server.fetch()
                status = self.server.status
                
                keys = ['domain', 'port', 'servid', 'software', 'slots', 'ram']
                
                infos = 'Current server data:\n' + \
                    '\n'.join(f'> *{key}*: **{getattr(self.server, key)}**'
                              for key in keys)
                
                await msg.reply(f'> **Server status: [ {status} ] **\n{infos}')
    
            case unhandled:
                '''
                Error handling
                '''
            
                await msg.reply(f'Unhandled or invalid syntax: `{" -> ".join(unhandled)}`.')
    
    def run(self) -> None:
        '''
        Wraps discord.Client.run to run the bot.
        '''
        
        super().run(self.conf['token'])


if __name__ == '__main__':
    Bot().run()

# EOF