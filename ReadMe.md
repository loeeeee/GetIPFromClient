# GetIP

## Intro
This script can act as three roles. Currently it only supports three machine acting as each role.
- Server, receiving IP address from client
- Client, reporting IP address to server
- Observer, viewing client IP address by communicating with server

## Quick start
- Download the code to all of your machine.
- Solve dependency.
- Run the code on one of the machine, the code will generate a config file.
- Change the **ROLE** in config file.
- Save the config for later copying and pasting.
- Paste the config into the same dir as the code on other machines.
- Change the **ROLE** in config.
- Change the config to your desire.

## Notes
- Do not forget to open ports at firewall.
- Client should work with crontab
- Server should work with systemd