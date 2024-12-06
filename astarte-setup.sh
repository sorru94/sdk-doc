#!/usr/bin/env bash

# (C) Copyright 2024, SECO Mind Srl
#
# SPDX-License-Identifier: Apache-2.0

set -eEuo pipefail

# Run the setup script non interactively.
ASTARTE_SETUP_NON_INTERACTIVE=${ASTARTE_SETUP_NON_INTERACTIVE:-false}
# Directory where to setup (clone) the Astarte repository.
ASTARTE_SETUP_CLONE_DIR=${ASTARTE_SETUP_CLONE_DIR:-"$HOME"}
# Base domain for the Astarte docker compose.
# When set to the default 'astarte.localhost' only simulated devices on the host machine
# will be able to connect to it. When set to 'astarte.<HOST IP ADDR>.nip.io' devices running
# on dedicated hardware but connected to the same LAN of the host machine will be able to
# connect to Astarte.
if [[ -n ${DOCKER_COMPOSE_ASTARTE_BASE_DOMAIN:-} ]]; then
    ASTARTE_SETUP_BASE_DOMAIN="$DOCKER_COMPOSE_ASTARTE_BASE_DOMAIN"
else
    ASTARTE_SETUP_BASE_DOMAIN=${ASTARTE_SETUP_BASE_DOMAIN:-'astarte.localhost'}
fi

# Global variable used to store the access token for the default 'test' realm
REALM_ACCESS_TOKEN=""
# Versions of Astarte and the Docker compose initializer used in the script
ASTARTE_VERSION="release-1.2"
COMPOSE_INIALIZER_VERSION="1.2.0"

# Funciton helper for the --help command
print_help() {
    echo "Usage: $0 [--clone-dir <clone_dir>] [--base-domain <base_domain>] [-y]"
    echo "Set up Astarte in the specified directory and configures it with the given base domain."
    echo ""
    echo "Options:"
    echo "  --clone-dir   Directory where Astarte will be cloned as 'astarte' (default: $ASTARTE_SETUP_CLONE_DIR)"
    echo "  --base-domain Base domain for Astarte (default: $ASTARTE_SETUP_BASE_DOMAIN)"
    echo "  -y            Non-interactive mode, automatically selects yes/default in all prompts"
    echo "  --help        Display this help message"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --clone-dir)
            ASTARTE_SETUP_CLONE_DIR="$2"
            shift 2
            ;;
        --base-domain)
            ASTARTE_SETUP_BASE_DOMAIN="$2"
            shift 2
            ;;
        -y)
            ASTARTE_SETUP_NON_INTERACTIVE=true
            shift 1
            ;;
        --help)
            print_help
            exit 0
            ;;
        *)
            echo "Invalid argument: $1"
            print_help
            exit 1
            ;;
    esac
done

if [ ! -d "$ASTARTE_SETUP_CLONE_DIR" ]; then
    echo "Provided clone directory does not exists: $ASTARTE_SETUP_CLONE_DIR."
    exit 1
fi
ASTARTE_SETUP_CLONE_DIR="$ASTARTE_SETUP_CLONE_DIR/astarte"

if [ ! -d "$ASTARTE_SETUP_CLONE_DIR" ]; then
    mkdir -p "$ASTARTE_SETUP_CLONE_DIR"
else
    # The clone directory is not empty
    count=$(find "$ASTARTE_SETUP_CLONE_DIR" -mindepth 1 -maxdepth 1 | wc -l)
    if [[ $count -ne 0 ]]; then
        echo "Provided clone directory directory already contains a non empty astarte folder."
        echo "This could be the result from a previous run of this script, it should be deleted before running this script again."
        exit 1
    fi
fi

# Ask for y|N
prompt() {
    read -rp "$1 (y/N) " p
    if [ "$p" == "y" ]; then
        p="y"
    else
        p="n"
    fi
}

# Prompt and then run the optional command
ask() {
    if $ASTARTE_SETUP_NON_INTERACTIVE; then
        $2
        return
    fi
    prompt "$1"
    if [ "$p" == "y" ]; then
        $2
    fi
}

# Prompt and then run the required command, or fail setup procedure
hard_ask() {
    if $ASTARTE_SETUP_NON_INTERACTIVE; then
        $2
        return
    fi
    prompt "$1"
    if [ "$p" == "y" ]; then
        $2
    else
        echo "Astarte setup aborted."
        exit 1
    fi
}

tell_and_wait() {
  echo "$1"
    if $ASTARTE_SETUP_NON_INTERACTIVE; then
        return
    fi
  read -r -p "Press Enter to continue..."
}

# Check the aio-max-nr for Scylla
check_aio_max() {
    aio_max_nr="$(sysctl -n fs.aio-max-nr || cat /proc/sys/fs/aio-max-nr)"
    if [[ $aio_max_nr -lt 1048576 ]]; then
        echo "You need to update the sys 'fs.aio-max-nr' to be atleast 1048576 to run ScyllaDB"
        echo "You can use the command:"
        echo "    sudo sysctl -w fs.aio-max-nr=1048576"
        echo
        exit 1
    fi
}

find_docker_compose() {
    if [[ -n ${DOCKER_COMPOSE:-} ]]; then
        echo "Using the '$DOCKER_COMPOSE' command" >&2
        return
    elif docker compose version; then
        export DOCKER_COMPOSE='docker compose'
    elif docker-compose version; then
        export DOCKER_COMPOSE='docker-compose'
    else
        echo "Couldn't run the 'docker-compose' nor 'docker compose' commands"
        echo "You can specify a by setting the DOCKER_COMPOSE env variable"
        exit 1
    fi
}

find_astartectl() {
    if ! command -v astartectl; then
        echo "Cannot find 'astartectl' in PATH" >&2
        echo "Please download and install the latest release for your system" >&2
        echo "You can find it here: https://github.com/astarte-platform/astartectl" >&2
        exit 1
    fi
}

clone_astarte() {
    git clone https://github.com/astarte-platform/astarte.git -b $ASTARTE_VERSION "$ASTARTE_SETUP_CLONE_DIR"
    cd "$ASTARTE_SETUP_CLONE_DIR"
}

run_docker_cmds() {
    docker_cleanup
    docker run -v "$(pwd)/compose:/compose" astarte/docker-compose-initializer:$COMPOSE_INIALIZER_VERSION
    $DOCKER_COMPOSE pull
    $DOCKER_COMPOSE up -d

    wait_astarte_healty
}

wait_astarte_healty() {
    printf "Astarte is initializing, waiting for cluster setup"
    while true; do
        if curl_get_status_ok "http://api.$ASTARTE_SETUP_BASE_DOMAIN/appengine/health" &&
            curl_get_status_ok "http://api.$ASTARTE_SETUP_BASE_DOMAIN/pairing/health" &&
            curl_get_status_ok "http://api.$ASTARTE_SETUP_BASE_DOMAIN/realmmanagement/health"; then

            printf "\nAstarte is ready.\n"
            break
        fi

        for _ in 1 2 3; do
            printf "."
            sleep 1
        done
        printf "\b\b\b   \b\b\b"
    done
}

curl_get_status_ok() {
    status=$(curl -s -o /dev/null -X GET -w "%{http_code}" "$1")

    if [[ $status =~ ^2.* ]]; then
        return 0
    fi

    return 1
}

gen_keys() {
    echo "Generating key-pair for the 'test' realm."
    astartectl utils gen-keypair test
}

create_realms() {
    success=0
    for _ in {1..5}; do
        if astartectl housekeeping realms create -y test \
            --astarte-url "http://api.$ASTARTE_SETUP_BASE_DOMAIN" \
            --realm-public-key "test_public.pem" \
            -k compose/astarte-keys/housekeeping_private.pem; then
            success=1
            break
        fi
        sleep 5
    done

    if [[ ! $success -eq 1 ]]; then
        docker_cleanup
        echo "Realm creation failure." >&2
        echo "Consider installing Astarte following the manual procedure." >&2
        exit 1
    fi
}

gen_token() {
    REALM_ACCESS_TOKEN=$(astartectl utils gen-jwt all-realm-apis -k "test_private.pem")
}

open_dashboard() {
    echo "To login use the realm 'test' and the previously generated token"
    xdg-open "http://dashboard.$ASTARTE_SETUP_BASE_DOMAIN"
}

docker_cleanup() {
    $DOCKER_COMPOSE down -v
}

main() {
    check_aio_max
    find_docker_compose
    find_astartectl

    echo -e "\nThe Astarte repository will be cloned in the directory: '$ASTARTE_SETUP_CLONE_DIR'."
    hard_ask "Continue?" clone_astarte

    echo -e "\nDocker compose will start all the required cointainers for Astarte."
    hard_ask "Continue?" run_docker_cmds

    echo -e "\nA new realm, named 'test' will be created."
    echo "Realms are isolated spaces whithin Astarte where devices can connect."
    tell_and_wait "Use the 'test' realm to connect your devices."

    gen_keys
    create_realms
    gen_token

    echo -e "\nRealm 'test' created successfully."
    echo "Generated access token for 'test' realm:"
    echo "$REALM_ACCESS_TOKEN"
    tell_and_wait "Use the access token to authenticate with Astarte."

    echo -e "\nAstarte has been correctly set up and started."
    echo "Astarte will continue to run untill it's stopped manually using 'docker compose down [-v]'."
    echo "You can use the Astarte dashboard to monitor the status of your Astarte instance."
    ask "Open the dashboard in your default browser?" open_dashboard
}

main
