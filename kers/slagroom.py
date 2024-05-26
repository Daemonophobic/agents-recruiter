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

from kers.apiClient import ApiClient
from kers.scanner import Scanner
from kers.breacher import Breacher
from kers.intruder import Intruder


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
        self._apiClient = ApiClient(self._config["API_URL"], self._config["JWT_TOKEN"])
        self._scanner = Scanner()
        self._breacher = Breacher()
        self._intruder = Intruder(self._apiClient)
        self._task_queue = queue.Queue()
        self._task = None
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

    def _fill_queue(self) -> None:
        tasks = self._apiClient.check_in()['commands']
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
                match task["command"]:
                    case 'scan':
                        print(f"[Slagroom] Scanning {task['ips']}")
                        output = self._scanner.scan_range(task["ips"], task["ports"])
                    case 'breach':
                        print(f"[Slagroom] Breaching {task['ips']}")
                        output = self._breacher.breach(task["ips"], task["ports"])
                        print(f"[Slagroom] Output: {output}")
                    case 'intrude':
                        print(f"[Slagroom] Intruding {task['ips']}")
                        output = self._intruder.intrude(task['ips'])
                        print(f"[Slagroom] Output: {output}")
                self._task_queue.task_done()
                time.sleep(self._wait_time)
            except KeyboardInterrupt:
                sys.exit(0)

    def start(self) -> None:
        print("[Slagroom] Starting Slagroom...")
        self._thread.start()
        self._thread.join()
