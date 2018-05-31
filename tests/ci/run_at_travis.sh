#!/usr/bin/env bash

export BOTO_CONFIG=/dev/null

if [ -z "$TOXENV" ]; then
    virtualenv .venv
    source .venv
    pip install -e ./
    rally db ensure
    rally env create --from-sysenv --name test_env
    rally task start "$XRALLY_TASK"
else
    tox
fi
