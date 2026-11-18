#!/bin/sh
set -eu

case "${1:-}" in
    ping)
        printf '%s\n' '{"protocol_version":"1.0","supported_tasks":[],"self_trained_rl":false,"preferred_speed_mps":null}'
        ;;
    *)
        printf '%s\n' 'Supported command: ping' >&2
        exit 64
        ;;
esac
