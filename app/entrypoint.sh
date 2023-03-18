#!/bin/bash

if [ "$@" = "debugpy" ]; then
	exec python -m debugpy --listen 0.0.0.0:5678 /app/bot.py
fi

if [ "$@" = "bot" ]; then
	exec python /app/bot.py
fi

exec "$@"
