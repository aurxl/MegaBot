import os
import pathlib
from dynaconf import Dynaconf, LazySettings
import argparse
from importlib.metadata import version, metadata

VERSION = version(str(__package__))
SCRIPT_PATH = pathlib.Path(__file__).parent.resolve()
LOGGING_DEFAULT_PATH = f"{SCRIPT_PATH.parent.resolve()}/log"
CONFIG_DEFAULT_PATHS = [
    "/etc/megabot",
    f"{os.path.expanduser('~')}/.conf/megabot",
    f"{SCRIPT_PATH.parent.resolve()}/config"
]
VALID_CONFIG_NAMES = ["megabot.yml", "megabot.yaml"]
REQUIRED_CONF_OPTIONS = [("Discord", "token"), ("w2g", "token")]
DEFAULT_DISCORD_SETTINGS = {
    "token": "",
    "prefix": "!",
    "owner": "",
    "admin": "",
    "mod": "",
    "blacklist": []
}
DEFAULT_W2G_SETTINGS = {
    "enable": False,
    "token": "",
    "channel": "",
    "streamer": ""
}
DEFAULT_LOGGING_SETTINGS = {
    "path": LOGGING_DEFAULT_PATH,
    "debug": False,
    "cli": {
        "level": 0
    }
}

argConsts = {
    "PROG": __package__,
    "DESCRIPTION": f"MegaBot v{VERSION} Discord music bot",
    "EPILOG": ""
}

class ConfigError(Exception):
    "Configuration not valid"

def __cli_args() -> argparse.Namespace:
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

def __config_settings() -> LazySettings:
    cli_options = __cli_args()
    config_paths = CONFIG_DEFAULT_PATHS

    if cli_options.CONF:
        config_paths = [cli_options.CONF]

    for path in config_paths:
        if os.path.exists(path):
            return Dynaconf(
                root_path=path,
                settings_files=VALID_CONFIG_NAMES,
                merge_enabled=True,
                discord=DEFAULT_DISCORD_SETTINGS,
                w2g=DEFAULT_W2G_SETTINGS,
                logging=DEFAULT_LOGGING_SETTINGS,
                yaml_loader="safe_load"
            )
    raise FileNotFoundError("No config file found")

def __merge_settings(file_config:LazySettings, cli_args:argparse.Namespace) -> None:
    if cli_args.DEBUG:
        file_config.logging.debug = True
    if cli_args.LOGGINGPATH:
        file_config.logging.path = cli_args.LOGGINGPATH
    if cli_args.VERBOSE:
        file_config.logging.cli.level = cli_args.VERBOSE

def __evaluate_settings(config:LazySettings) -> None:
    assert config.discord, "Discord Key is defined, but no values assigned"
    assert config.w2g, "W2G Key is defined, but no values assigned"
    assert config.w2g, "W2G Key is defined, but no values assigned"

    assert config.discord.token, "Discord token required"
    assert config.w2g.token, "W2G token required"

def __settings() -> LazySettings:
    config = __config_settings()
    if not config:
        raise FileNotFoundError("No config file found")
    cli_args = __cli_args()
    __merge_settings(config, cli_args)
    __evaluate_settings(config)

    return config

settings = __settings()
