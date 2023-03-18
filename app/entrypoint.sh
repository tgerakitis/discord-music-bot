#!/bin/bash

if [ -z "$@" ]; then
	echo "please provide a command, 'debugpy' for debugging or 'bot' for production mode or any other shell command"
	exit
fi

baseFolder="/app"

if [ "$@" = "debugpy" ]; then
	exec python -m debugpy --listen 0.0.0.0:5678 ${baseFolder}/bot.py
elif [ "$@" = "bot" ]; then
	exec python -O ${baseFolder}/bot.py
fi

exec "$@"
