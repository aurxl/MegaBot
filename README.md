# A very simple Discord Bot.

A Bot for playing music from YouTube.
Very stable. Meant to be run on Server.

## Usage
1. go to install dir and execute `poetry install`
2. start bot with `poetry run python discordBot.py`
or start and enable service:
    - copy `MegaBot.service` to `/etc/systemd/system`
    ```
        sudo cp MegaBot.service /etc/systemd/system/MegaBot.service
    ```
    - enable service
    ```
        sudo systemctl enable MegaBot.servcie
    ```
    - start service
    ```
        sudo systemctl start MegaBot.service
    ```