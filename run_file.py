# -*- coding: utf-8 -*-

from rqalpha import run_file

config = {
  "base": {
    "start_date": "2022-01-01",
    "end_date": "2022-01-26"
  },
  "extra": {
    "log_level": "verbose",
  },
  "mod": {
    "sys_analyser": {
      "enabled": False
    }
  },
}

strategy_file_path = "./magic.py"

run_file(strategy_file_path, config)
