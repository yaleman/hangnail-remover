#!/bin/bash

mkdir -p ~/.ssh/

echo "${GITHUB_KEY}" > ~/.ssh/github.com

chmod 0600 ~/.ssh/github.com

cat > ~/.ssh/config <<-EOM

Host github.com
  User git
  StrictHostKeyChecking no
  UserKnownHostsFile=/dev/null
  IdentityFile /home/splunk/.ssh/github.com

EOM

git clone 'git@github.com:rms-support-letter/rms-support-letter.github.io.git' sourcerepo
