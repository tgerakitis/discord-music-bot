#!/bin/bash

if [ -z "$@" ]; then
	echo "please provide a command, 'debugpy' for debugging or 'bot' for production mode or any other shell command"
	exit
fi
botFile="app/bot.py"
if [ "$@" = "debugpy" ]; then
	echo "launching dev mode"
	exec python -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:5678 $botFile
elif [ "$@" = "bot" ]; then
	echo "launching prod mode"
	exec python -O $botFile
fi

echo "launching custom script"
exec "$@"
