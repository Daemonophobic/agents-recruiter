"""
This module implements the main functionality of kers.

Authors:
- Marijn van Dijk
- Tom Buis
"""

import os
import codecs
import json
import threading
import queue
import time
import uuid

from kers.apiClient import ApiClient
from kers.scanner import Scanner


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

        self._apiClient = ApiClient(self._config["API_URL"], self._config["JWT_TOKEN"])
        self._scanner = Scanner()
        self._task = None
        self._scanner.scan_range(["45.33.32.156"], [443])

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

    def _worker(self) -> None:
        while True:
            if self._task is None:
                return
            else:
                return

    def start(self) -> None:
        # self._thread.start()
        return