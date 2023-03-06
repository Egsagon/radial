import mcstatus

ip = 'LeServeurDuFutur1.aternos.me'

class Fetcher:
    
    def using_mcstatus(ip: str) -> tuple[str]:
        '''
        Fetch the server status using mcstatus,
        Aka ping the server.
        '''
        
        server = mcstatus.JavaServer.lookup(ip)
        status = server.status()
    
        return (status.description.split('\n')[0].split()[-1][:-1],
                status.players.online)
    
    def using_aternos(sv: object) -> tuple[str]:
        '''
        Fetch the server status using aternos api,
        which is rate limited. Bot can raise a
        teapot error.
        '''
        
        sv.fetch()
        return sv.status, sv.players_count

def format(status: str, count: int) -> str:
    '''
    Format a data string for the bot
    discord presence.
    '''
    
    online = status == 'online'
    
    return f"{status.upper()} {f'(#{count})' if online else ''}"

# EOF