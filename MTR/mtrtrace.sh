#!/usr/bin/env bash
IP=$1
mtr -r -c3 -w -b $IP
