# -*- coding: utf-8 -*-

from rqalpha import run_file

config = {
  "base": {
    "start_date": "2021-10-01",
    "end_date": "2021-11-30"
  },
  "extra": {
    "log_level": "warning",
  },
  "mod": {
    "sys_analyser": {
      "enabled": False
    }
  },
}

strategy_file_path = "./magic.py"

run_file(strategy_file_path, config)
