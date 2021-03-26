#!/bin/bash

cd "$HOME/hangnail-remover/" || exit 1

git pull
python3 hangnail_inspector.py --update

git add results/
git commit -am "update $(date +%Y-%m-%d-%H:%M)"
git push

