import aiohttp
import asyncio
import logging
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

class ServerMonitor:
    def __init__(self):
        self.api_url = "http://api.blackrussia.online/servers.json"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Cache-Control": "no-cache"
        }
        self.servers = []
        self.last_update = None
        self.last_data_hash = None

    async def fetch_servers(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data
        except Exception as e:
            logging.error(f"Request error: {str(e)}")
            return None

    def process_data(self, raw_data):
        processed = []
        if isinstance(raw_data, list):
            for item in raw_data:
                try:
                    processed.append({
                        'name': str(item.get('name', 'Unknown')).strip(),
                        'ip': str(item.get('ip', '0.0.0.0')).strip(),
                        'port': int(item.get('port', 0)),
                        'online': int(item.get('online', 0))
                    })
                except Exception as e:
                    logging.error(f"Processing error: {str(e)}")
        return processed

    def has_changes(self, new_data):
        current_hash = hash(str(new_data))
        if current_hash != self.last_data_hash:
            self.last_data_hash = current_hash
            return True
        return False

async def display_servers(monitor, update_status):
    
    if monitor.servers:
        max_name_len = max(len(s['name']) for s in monitor.servers) + 2
        table_width = max_name_len + 19 + 9 + 11

        print(f"{Fore.BLUE}┌{'─' * table_width}┐")
        print(f"│ {Fore.YELLOW}{'Сервер':^{max_name_len}} {Fore.BLUE}│ {Fore.YELLOW}{'IP-адрес':^15} {Fore.BLUE}│ {Fore.YELLOW}{'Порт':^5} {Fore.BLUE}│ {Fore.YELLOW}{'Онлайн':^7} {Fore.BLUE}│")
        print(f"├{'─' * table_width}┤")

        for server in monitor.servers:
            online = server['online']
            color = Fore.GREEN if online > 0 else Fore.RED
            print(
                f"{Fore.BLUE}│ {color}{server['name']:<{max_name_len}}{Fore.BLUE}│ "
                f"{Fore.WHITE}{server['ip']:^15} {Fore.BLUE}│ "
                f"{Fore.WHITE}{server['port']:^5} {Fore.BLUE}│ "
                f"{color}{online:^7}{Fore.BLUE}│"
            )
        print(f"└{'─' * table_width}┘")
        
    status_color = Fore.GREEN if update_status else Fore.YELLOW
    status_message = "Current data 🟢" if update_status else "UPDATE..."
    
    if monitor.last_update:
        update_time = monitor.last_update.strftime("%H:%M:%S")
        print(f"\n{status_color}{status_message} {Fore.CYAN}| Last update: {update_time}")
    else:
        print(f"\n{status_color}{status_message}")
    

async def main():
    monitor = ServerMonitor()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        filename='server_monitor.log'
    )

    try:
        while True:
            raw_data = await monitor.fetch_servers()
            if raw_data:
                new_data = monitor.process_data(raw_data)
                has_changes = monitor.has_changes(new_data)
                
                if has_changes:
                    monitor.servers = new_data
                    monitor.last_update = datetime.now()
                
                await display_servers(monitor, update_status=not has_changes)
            
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Monitoring stopped{Style.RESET_ALL}")

if __name__ == "__main__":
    asyncio.run(main())
