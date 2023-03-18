#!/bin/bash

if [ -z "$@" ]; then
	echo "please provide a command, 'debugpy' for debugging or 'bot' for production mode or any other shell command"
	exit
fi

botFile="/workspace/app/bot.py"
if [ "$@" = "debugpy" ]; then
	echo "launching dev mode"
	cd /workspace/app
	exec python -m debugpy --listen 0.0.0.0:5678 $botFile
elif [ "$@" = "bot" ]; then
	echo "launching prod mode"
	cd /workspace/app
	exec python -O $botFile
fi

echo "launching custom script"
exec "$@"
