#!/usr/bin/env python3
"""Bangs in DDG style without using DDG but just Rofi.

Load a JSON config file to have the bangs available. Rofi should return, using
its dmenu option, the handle followed by your query, e.g. "w burger" if you
want a Wikipedia article for "burger", or at least a much needed
disambiguationâ€¦

Config file example:
    { "bangs": [ {
        "handle": "w",
        "name": "Wikipedia",
        "url": "https://en.wikipedia.org/wiki/Special:Search?search={}&go=Go"
    } ] }

By default this scripts attempts to load your config file from
`~/.config/rofibangs.json`, but you can specify the ROFIBANGS_CONFIG_PATH
environment variable or pass the path through the -c command-line option.
"""

import argparse
import json
import os
import subprocess
import urllib.parse
import webbrowser


def load_config(config_path=None):
    if config_path is None:
        config_path = os.environ.get(
            "ROFIBANGS_CONFIG_PATH",
            os.path.expanduser("~/.config/rofibangs.json")
        )
    try:
        with open(config_path, "rt") as bangs_file:
            return json.load(bangs_file)
    except OSError:
        return None


def list_bangs(config):
    for item in config["bangs"]:
        name = item["name"]
        handle = item["handle"]
        print(f"- {handle} {name}")


def run_rofi(config, input_text="", title="bang"):
    rofi_path = config.get("rofi_path", "rofi")
    completed_process = subprocess.run(
        [rofi_path, "-dmenu", "-p", title],
        text=True,
        capture_output=True,
        input=input_text
    )
    output = completed_process.stdout
    if not output:
        exit("Empty Rofi output.")
    return output


def open_bang(config, handle, query):
    for bang in config["bangs"]:
        if handle == bang["handle"]:
            break
    else:
        print("Unknown handle.")
        return
    url = bang["url"].format(urllib.parse.quote(query.strip()))
    webbrowser.open_new_tab(url)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
            "-c", "--config", help="path to JSON config file"
    )
    ap.add_argument(
            "-l", "--list", action="store_true", help="show available bangs"
    )
    args = ap.parse_args()

    config = load_config()
    if config is None:
        exit("Can't load config file.")

    if args.list:
        list_bangs(config)
        return

    process_input = "\n".join(i["handle"] for i in config["bangs"]) + "\n"
    output = run_rofi(config, input_text=process_input)
    parts = output.split(maxsplit=1)
    if len(parts) < 1:
        exit("Bad Rofi output.")
    if len(parts) == 1:
        handle = parts[0]
        query = run_rofi(config, title=handle)
    else:
        handle, query = parts
    open_bang(config, handle, query)


if __name__ == "__main__":
    main()
