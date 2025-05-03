from multiprocessing import Process, Lock

from config import config
from proxy.request_handler import RequestHandler
from proxy.tcp_server import TCPServer


class ProxyNotFound(Exception):
    def __init__(self, proxy_id: int):
        super().__init__(f"Proxy with ID {proxy_id} was not found")


def _run_proxy():
    # Initialise TCPServer
    server: TCPServer | None
    try:
        server = TCPServer((config.host, config.port), RequestHandler)
        print(f"Running proxy on {config.host}:{config.port}",
              f"Forwarding for {config.real_host}:{config.real_port}",
              sep="\n")

        server.serve_forever()
    except OSError as e:
        print(f"OS Error starting server: {str(e)}")
        exit(e.errno)


class _ProxyManager:
    proxies_lock = Lock()
    proxies: list[Process] = []

    def cleanup(self):
        # Terminate proxy servers when this object is deleted
        for process in self.proxies:
            process.terminate()
            process.join()
            process.close()

    def get_new_id(self) -> int | None:
        # Either find the first empty spot in the list or return the max
        for i in range(len(self.proxies)):
            if self.proxies[i].exitcode is not None:
                return i

        return None

    async def new(self):
        # Create new process and add it to the list
        with self.proxies_lock:
            proxy_id = self.get_new_id()
            process = Process(target=_run_proxy)

            if proxy_id is None:
                self.proxies.append(process)
                proxy_id = len(self.proxies) - 1
            else:
                self.proxies[proxy_id].join()
                self.proxies[proxy_id].close()
                self.proxies[proxy_id] = process
        
        process.start()
        return proxy_id

    def terminate(self, proxy_id: int):
        # If the process_id doesn't point to a process, raise HTTP 404
        if proxy_id > len(self.proxies)-1 or self.proxies[proxy_id].exitcode is not None:
            raise ProxyNotFound(proxy_id)
        
        # Get the proxy and assert its existence as it should exist
        proxy = self.proxies[proxy_id]
        assert proxy

        # Terminate and join the process
        proxy.terminate()
        proxy.join()


proxy_manager = _ProxyManager()
