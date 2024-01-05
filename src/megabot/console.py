#!/usr/bin/env python
import argparse
import configparser
import discord
import logging
import logging.handlers
import os

from importlib.metadata import version


VERSION = version(__package__)
DEFAULTCONF = ("/etc/megabot.conf", f"{os.path.expanduser('~')}/.config/megabot.conf")
DEFAULTLOGLEVEL = "INFO"
DEFAULTLOGPATH = "./log/"
REQCONFOPTS = [("Discord", "token")]
argConsts = {
    "PROG": __package__,
    "DESCRIPTION": f"MegaBot v{VERSION} Discord music bot",
    "EPILOG": ""
}


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
        "-l",
        "--logging",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        dest="LOGGING",
        help="set logging level"
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
        help=f"path to config file (defaults: {DEFAULTCONF[0]} or {DEFAULTCONF[1]})",
        type=str,
        dest='CONF'
    )
    return parser.parse_args()


def parse_config(path):
    # check if given path exists
    if not path:
        for item in DEFAULTCONF:
            if os.path.isfile(item):
                path = item
                break

    if not path:
        raise Exception(f"No config file at default locations {DEFAULTCONF}")
    elif not os.path.isfile(path):
        raise Exception(f"No config file at {path}")

    config = configparser.ConfigParser()
    try:
        config.read(path)
    except Exception as exc:
        print(exc)
        exit(1)

    for opt in REQCONFOPTS:
        try:
            assert config[opt[0]][opt[1]]
        except KeyError:
            raise Exception(f"missing {opt} in config")

    return config


def evaluate_options(args, conf):
    opts = {
        "Discord": {
            "token": conf["Discord"]["token"],
        },
        "w2g": {},
        "system": {},
    }

    if "w2g" in conf:
        w2g_conf = conf["w2g"]
        try:
            opts["w2g"]["token"] = w2g_conf["token"]
        except KeyError:
            pass

    if "system" in conf:
        system_conf = conf["system"]
        try:
            opts["system"]["logging-level"] = system_conf["logging-level"]
        except KeyError:
            pass
        try:
            opts["system"]["logging-path"] = system_conf["logging-path"]
        except KeyError:
            pass

    if args.LOGGING:
        opts["system"]["logging-level"] = args.LOGGING
    if args.LOGGINGPATH:
        opts["system"]["logging-path"] = args.LOGGINGPATH

    # check for missing options set defaults
    if "logging-level" not in opts["system"].values():
        opts["system"]["logging-level"] = DEFAULTLOGLEVEL
    if "logging-path" not in opts["system"].values():
        opts["system"]["logging-path"] = DEFAULTLOGPATH

    return opts


def setup_logging(logging_opts):
    if not os.path.exists(logging_opts["logging-path"]):
        try:
            os.mkdir(logging_opts["logging-path"])
        except Exception as exc:
            raise Exception(f"cant create directory {logging_opts['logging-path']}") from exc

    logger = logging.getLogger('megabot')
    logger.setLevel(logging_opts['logging-level'])
    logging.getLogger('discord.http').setLevel(logging_opts['logging-level'])

    handler = logging.handlers.RotatingFileHandler(
        filename=f"{logging_opts['logging-path']}/megabot.log",
        encoding='utf-8',
        maxBytes=32 * 1024,  # 32 KiB
        backupCount=7
    )
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter("[{asctime}] {levelname:<8} -> {name}: {message}", datefmt=date_format, style="{")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def main() -> None:
    args = parse_args()
    conf = parse_config(path=args.CONF)
    opts = evaluate_options(conf=conf, args=args)
    logging = setup_logging(opts["system"])


if __name__ == "__main__":
    main()
