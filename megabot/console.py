#!/usr/bin/env python
import argparse
import configparser
import logging
import os
import pathlib
import sys
from importlib.metadata import version
from logging.handlers import RotatingFileHandler

VERSION = version(__package__)
SCRIPT_PATH = pathlib.Path(__file__).parent.resolve()
CONFIG_DEFAULT_PATHS = [
    "/etc/megabot/megabot.conf",
    f"{os.path.expanduser('~')}/.conf/megabot/megabot.conf",
    f"{SCRIPT_PATH.parent.resolve()}/config/megabot.conf"
]
LOGGING_DEFAULT_PATH = f"{SCRIPT_PATH.parent.resolve()}/log"
LOGGING_DEFAULT_LEVEL = "INFO"
REQUIRED_CONF_OPTIONS = [("Discord", "token"), ("w2g", "token")]
argConsts = {
    "PROG": __package__,
    "DESCRIPTION": f"MegaBot v{VERSION} Discord music bot",
    "EPILOG": ""
}


logger = logging.getLogger('megabot')
logger.setLevel(logging.DEBUG)

class ConfigParser(configparser.ConfigParser):
    def __getitem__(self, key):
        if key != self.default_section and not self.has_section(key):
            raise KeyError(key)

        return {_: self.__strip_outer_quotes(value=self._proxies[key][_]) for _ in self._proxies[key]}

    @staticmethod
    def __strip_outer_quotes(value):
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        return value


def parse_args():
    parser = argparse.ArgumentParser(
        prog=argConsts['PROG'],
        description=argConsts['DESCRIPTION'],
        epilog=argConsts['EPILOG'],
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--version", action="version", version=f"{VERSION}")
    parser.add_argument("-v", "--verbose", action="count", default=0, dest="VERBOSE", help="set verbosity level")
    parser.add_argument(
        "-d",
        "--file-logging-debug",
        action="store_true",
        dest="DEBUG",
        help="Enable Debug logging for log files."
    )
    parser.add_argument(
        "-p",
        "--logging-path",
        dest="LOGGINGPATH",
        help="set logging path"
    )
    parser.add_argument(
        "-c",
        "--config",
        help=f"path to config file (defaults: {CONFIG_DEFAULT_PATHS})",
        type=str,
        dest='CONF'
    )
    return parser.parse_args()


def read_config(cli_path: str):
    if cli_path:
        paths = [cli_path]
    else:
        paths = CONFIG_DEFAULT_PATHS

    config = ConfigParser()

    # Loading config file
    for path in paths:
        if os.path.isfile(path):
            config.read(path)
            if not config.sections():
                print(f"Found empty conf in {path}")
                continue
            print(f"Loading Config file {path}")
            break
        continue
    if not config.sections():
        print(f"No config found in " + ", ".join(paths))
        exit(1)

    for opt in REQUIRED_CONF_OPTIONS:
        try:
            assert config[opt[0]][opt[1]]
        except KeyError:
            print(Exception(f"Missing {opt} in config"))
            exit(1)

    return config


def evaluate_options(args, conf):
    opts = {
        "Discord": {
            "token": conf["Discord"]["token"],
        },
        "w2g": {},
        "logging": {},
    }

    if "w2g" in conf:
        w2g_conf = conf["w2g"]
        try:
            opts["w2g"]["token"] = w2g_conf["token"]
        except KeyError:
            pass

    if "logging" in conf:
        logging_conf = conf["logging"]
        try:
            opts["logging"]["debug"] = logging_conf["debug"]
        except KeyError:
            pass
        try:
            opts["logging"]["path"] = logging_conf["path"]
        except KeyError:
            pass

    opts["logging"]["debug"] = args.DEBUG
    if args.LOGGINGPATH:
        opts["logging"]["path"] = args.LOGGINGPATH
    opts["logging"]["cli-level"] = args.VERBOSE

    # check for missing options set defaults
    if "debug" not in opts["logging"].keys():
        opts["logging"]["debug"] = False
    if "path" not in opts["logging"].keys():
        opts["logging"]["path"] = LOGGING_DEFAULT_PATH

    return opts


def setup_logging(logging_opts):
    if not os.path.exists(logging_opts["path"]):
        try:
            os.mkdir(logging_opts["path"])
        except Exception as exc:
            raise Exception(f"cant create directory {logging_opts["path"]}") from exc

    # Initialize file logging
    file_handler = RotatingFileHandler(
        filename=f"{logging_opts["path"]}/megabot.log",
        encoding='utf-8',
        maxBytes=32 * 1024,  # 32 KiB
        backupCount=7
    )

    # Initialize stream logging
    stream_handler = logging.StreamHandler(sys.stdout)

    # Set formatter
    date_format_file = "%Y-%m-%d %H:%M:%S"
    date_format_stream = "%H:%M:%S"
    file_formatter = logging.Formatter(
        "[{asctime}] {levelname:<8} -> {name}: {message}",
        datefmt=date_format_file,
        style="{"
    )
    stream_formatter = logging.Formatter(
        "[{asctime}] {levelname:<8} -> {name}: {message}",
        datefmt=date_format_stream,
        style="{"
    )
    file_handler.setFormatter(file_formatter)
    stream_handler.setFormatter(stream_formatter)

    # Determine logging level for file handler
    if logging_opts["debug"]:
        logging.getLogger('discord.http').setLevel(logging.DEBUG)
        file_handler.setLevel(logging.DEBUG)
    else:
        logging.getLogger('discord.http').setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)

    # Determine logging level for stream handler
    if logging_opts["cli-level"] == 0:
        stream_handler.setLevel(logging.WARNING)
    elif logging_opts["cli-level"] == 1:
        stream_handler.setLevel(logging.INFO)
    elif logging_opts["cli-level"] == 2:
        stream_handler.setLevel(logging.DEBUG)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


def main() -> None:
    args = parse_args()
    conf = read_config(cli_path=args.CONF)
    opts = evaluate_options(conf=conf, args=args)
    setup_logging(opts["logging"])
    logger.info("Hello World!")


if __name__ == "__main__":
    main()
