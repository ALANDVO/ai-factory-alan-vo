#!/bin/bash
# auto_push.sh — Runs every 10 minutes, pushes the next unpushed app
# Cron: */10 * * * * /home/alanvo/ai-factory/auto_push.sh >> /home/alanvo/ai-factory/auto_push.log 2>&1

export PATH="$HOME/bin:$PATH"
cd ~/ai-factory
python3 factory.py 2>&1
