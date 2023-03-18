#!/bin/bash

if [ -z "$@" ]; then
	echo "please provide a command, 'debugpy' for debugging or 'bot' for production mode or any other shell command"
	exit
fi

if [ "$@" = "debugpy" ]; then
	echo "launching dev mode"
	exec python -m debugpy --listen 0.0.0.0:5678 /workspace/app/bot.py
elif [ "$@" = "bot" ]; then
	echo "launching prod mode"
	exec python -O /app/bot.py
fi

echo "launching custom script"
exec "$@"
