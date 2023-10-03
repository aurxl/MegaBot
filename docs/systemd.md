# configure systemd

## Usage
- create `megabot.service` in `/etc/systemd/system/`
- enable and start service: `systemctl enable megabot.service && systemctl start megabot.service` 
#### sample unit file:
``` ini
[Unit]
Description=MegaBot
After=network.target

[Service]
Type=forking
User=dcbots
Group=dcbots
WorkingDirectory=/home/dcbots/bots/MegaBot/

ExecStart=/usr/bin/screen -dmS MegaBot /home/dcbots/.local/bin/poetry run python discordBot.py
ExecStop=/usr/bin/screen -p 0 -S discordBot -X eval 'stuff \"^c\"\015'
 
RestartSec=5
Restart=always

[Install]
WantedBy=multi-user.target
```
