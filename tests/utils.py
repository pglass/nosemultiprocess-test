import os
import time
import logging

LOG = logging.getLogger(__name__)

def wait():
    time.sleep(2)

def debug_pid():
    LOG.info("Parent PID:  %s", os.getppid())
    LOG.info("Current PID: %s", os.getpid())
