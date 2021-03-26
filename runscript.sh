#!/bin/bash

cd "$HOME/hangnail-remover/" || exit 1

git -C "$HOME/hangnail-remover/" reset --hard
git -C "$HOME/hangnail-remover/" pull
git -C "$HOME/hangnail-remover/sourcerepo/" reset --hard
git -C "$HOME/hangnail-remover/sourcerepo/" pull

python3 hangnail_inspector.py --update

git add hangnail_data.json
git commit -am "update $(date +%Y-%m-%d-%H:%M)"
git push

