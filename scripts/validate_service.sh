#!/bin/sh
echo "sudo systemctl restart codedeploy-agent" | at -M now + 2 minute;