#!/usr/bin/env bash

rally db ensure
rally env create --from-sysenv --name test_env
rally task start "$XRALLY_TASK"
