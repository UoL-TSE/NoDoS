import asyncio
from multiprocessing import Process, Lock, process
from typing import Any, Callable

from fastapi import HTTPException

from config import config
from proxy.request_handler import RequestHandler
from proxy.tcp_server import TCPServer

def _run_proxy():
    # Initialise TCPServer
    try:
        server = TCPServer((config.host, config.port), RequestHandler)
        print(f"Running proxy on {config.host}:{config.port}",
              f"Forwarding for {config.real_host}:{config.real_port}",
              sep="\n")

        server.serve_forever()
    except OSError as e:
        print(f"OS Error starting server: {str(e)}")


class _ProxyManager:
    proxies_lock = Lock()
    proxies: list[Process] = []

    def __del__(self):
        # Terminate proxy servers when this object is deleted
        for process in self.proxies:
            if not process:
                continue

            process.terminate()
            process.join()

    def get_new_id(self) -> int | None:
        # Either find the first empty spot in the list or return the max
        for i in range(len(self.proxies)):
            if not self.proxies[i].is_alive():
                return i

        return None

    async def new(self):
        # Create new process and add it to the list
        with self.proxies_lock:
            proxy_id = self.get_new_id()
            process = Process(target=_run_proxy)

            if not proxy_id:
                self.proxies.append(process)
                proxy_id = len(self.proxies) - 1
            else:
                self.proxies[proxy_id] = process
        
        process.start()
        print(self.proxies)
        return proxy_id

    async def terminate(self, proxy_id: int):
        # If the process_id doesn't point to a process, raise HTTP 404
        if proxy_id > len(self.proxies) or self.proxies[proxy_id] is None:
            raise HTTPException(status_code=404, detail=f"Process with id {proxy_id} was not found.")
        
        # Get the proxy and assert its existence as it should exist
        proxy = self.proxies[proxy_id]
        assert proxy

        # Terminate and join the process
        proxy.terminate()
        proxy.join()


proxy_manager = _ProxyManager()
