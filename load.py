"""
Plugin for "HITS"
"""
import json
import os
import urllib

import requests
import sys
import time

SERVER = "edmc.edhits.space"

_thisdir = os.path.abspath(os.path.dirname(__file__))
_overlay_dir = os.path.join(os.path.dirname(_thisdir), "EDMCOverlay")
if _overlay_dir not in sys.path:
    sys.path.append(_overlay_dir)


import edmcoverlay
_overlay = None


def plugin_start():
    """
    Start up our EDMC Plugin
    :return:
    """
    global _overlay
    _overlay = edmcoverlay.Overlay()
    time.sleep(2)
    notify("ED:HITS Plugin Loaded")

HEADER = 510
INFO = 540
DETAIL1 = INFO + 25
DETAIL2 = DETAIL1 + 25
DETAIL3 = DETAIL2 + 25


def display(text, row=HEADER, col=80, color="yellow", size="large"):
    try:
        _overlay.send_message("hits_{}_{}".format(row, col),
                              text,
                              color,
                              80, row, ttl=4, size=size)
    except:
        pass


def header(text):
    display(text, row=HEADER, size="normal")


def notify(text):
    display(text, row=INFO, color="#00ff00", col=95)


def warn(text):
    display(text, row=INFO, color="red", col=95)


def info(line1, line2=None, line3=None):
    display(line1, row=DETAIL1, col=95, size="normal")
    if line2:
        display(line2, row=DETAIL2, col=95, size="normal")
    if line3:
        display(line3, row=DETAIL3, col=95, size="normal")


def journal_entry(cmdr, system, station, entry, state):
    """
    Check a system for advice
    :param cmdr:
    :param system:
    :param station:
    :param entry:
    :param state:
    :return:
    """
    if entry["event"] in ["StartJump"]:
        sysname = entry["StarSystem"]
        header("Checking HITS for {}".format(sysname))
        check_location(sysname)
    if entry["event"] in ["SendText"]:
        if entry["Message"]:
            cmd = entry["Message"]
            if cmd.startswith("!location"):
                if " " in cmd:
                    cmd, system = cmd.split(" ", 1)
                check_location(system)


def check_location(system):
    """
    Get a status report for a system
    :param system:
    :return:
    """
    resp = requests.get("http://{}/hits/v1/location/{}?hours=24".format(SERVER, urllib.quote(system)))

    if resp and resp.status_code == 200:
        data = json.loads(resp.content)
        if "advice" in data:
            if data["advice"]:
                warn(data["advice"])
            else:
                notify("System '{}' is verified low risk.".format(system))

        if "totalVisits" in data:
            info("Data for last {} hrs".format(data["periodHours"]),
                 "{} destroyed".format(data["destroyed"]),
                 "{} arrived safely".format(data["arrived"]))