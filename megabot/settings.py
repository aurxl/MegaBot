import os
import pathlib
from dynaconf import Dynaconf, LazySettings
import argparse
from importlib.metadata import version, metadata
from typing import List, Tuple, Dict, Any

VERSION: str = version(str(__package__))
SCRIPT_PATH: pathlib.Path = pathlib.Path(__file__).parent.resolve()
LOGGING_DEFAULT_PATH: str = f"{SCRIPT_PATH.parent.resolve()}/log"
CONFIG_DEFAULT_PATHS: List[str] = [
    "/etc/megabot",
    f"{os.path.expanduser('~')}/.conf/megabot",
    f"{SCRIPT_PATH.parent.resolve()}/config"
]
VALID_CONFIG_NAMES: List[str] = ["megabot.yml", "megabot.yaml"]
REQUIRED_CONF_OPTIONS: List[Tuple[str, str]] = [("Discord", "token"), ("w2g", "token")]

DEFAULT_DISCORD_SETTINGS: Dict[str, str] = {
    "token": "",
    "prefix": "!",
}
DEFAULT_MEGABOT_SETTINGS: Dict[str, str] = {
    "datapath": "/opt/megabot",
    "default_status": "discord"
}
DEFAULT_CORE_SETTINGS: Dict[str, bool] = {
    "enabled": True
}
DEFAULT_VOICE_SETTINGS: Dict[str, bool] = {
    "enabled": False
}
DEFAULT_MUSIC_SETTINGS: Dict[str, Any] = {
    "enabled": False,
    "mediapath": "",
    "yt_dlp": {
        "cookies": False,
        "cookiefile": ""
    }
}
DEFAULT_W2G_SETTINGS: Dict[str, Any] = {
    "enabled": False,
    "token": ""
}
DEFAULT_LOGGING_SETTINGS: Dict[str, Any] = {
    "path": LOGGING_DEFAULT_PATH,
    "debug": False,
    "cli": {
        "level": 0
    }
}
DEFAULT_MODULES_SETTINGS: Dict[str, Dict] = {
    "core": DEFAULT_CORE_SETTINGS,
    "voice": DEFAULT_VOICE_SETTINGS,
    "music": DEFAULT_MUSIC_SETTINGS,
    "w2g": DEFAULT_W2G_SETTINGS
}

argConsts: Dict[str, str] = {
    "PROG": str(__package__),
    "DESCRIPTION": f"MegaBot v{VERSION} Discord music bot",
    "EPILOG": ""
}

class ConfigError(Exception):
    "Configuration not valid"

def __cli_args() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
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
    cli_options: argparse.Namespace = __cli_args()
    config_paths: List[str] = CONFIG_DEFAULT_PATHS

    if cli_options.CONF:
        config_paths = [cli_options.CONF]

    for path in config_paths:
        if os.path.exists(path):
            return Dynaconf(
                root_path=path,
                settings_files=VALID_CONFIG_NAMES,
                merge_enabled=True,
                discord=DEFAULT_DISCORD_SETTINGS,
                megabot=DEFAULT_MEGABOT_SETTINGS,
                logging=DEFAULT_LOGGING_SETTINGS,
                modules=DEFAULT_MODULES_SETTINGS,
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

    assert config.discord.token, "Discord token required"
    if config.modules.w2g.enabled:
        assert config.modules.w2g.token, "W2G token required"

def __settings() -> LazySettings:
    config: LazySettings = __config_settings()
    if not config:
        raise FileNotFoundError("No config file found")
    cli_args: argparse.Namespace = __cli_args()
    __merge_settings(config, cli_args)
    __evaluate_settings(config)

    return config

settings: LazySettings = __settings()
