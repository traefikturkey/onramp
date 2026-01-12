#!/usr/bin/env bash
#
# bootstrap.sh - Prepare system for OnRamp (installs Docker and dependencies)
#
# This script is called automatically by `make install` on fresh systems,
# or can be run directly: ./bootstrap.sh
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Ensure we're in the onramp directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

log_info "OnRamp Bootstrap Script"
log_info "======================="

# Check if running as root (we need sudo, not root)
if [[ $EUID -eq 0 ]]; then
    log_error "Do not run this script as root. Run as a regular user with sudo access."
    exit 1
fi

# Check for sudo access
if ! sudo -v; then
    log_error "This script requires sudo access."
    exit 1
fi

# Keep sudo alive for the duration of the script
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

export DEBIAN_FRONTEND=noninteractive

# ============================================================================
# Step 1: System packages
# ============================================================================
log_info "Step 1: Installing system packages..."

# Update apt cache first
sudo apt update

# Detect Ubuntu using /etc/os-release (lsb_release may not exist on minimal installs)
IS_UBUNTU=false
if [[ -f /etc/os-release ]]; then
    # shellcheck source=/dev/null
    . /etc/os-release
    [[ "$ID" == "ubuntu" ]] && IS_UBUNTU=true
fi

# On Ubuntu, add Ansible PPA for latest version (requires software-properties-common)
if [[ "$IS_UBUNTU" == "true" ]]; then
    if ! apt-cache policy | grep -q "ansible/ansible"; then
        log_info "Adding Ansible PPA (requires software-properties-common)..."
        sudo apt install -y software-properties-common
        sudo apt-add-repository ppa:ansible/ansible -y
        sudo apt update
    fi
fi

PACKAGES=(
    git
    nano
    jq
    python3-pip
    yamllint
    python3-pathspec
    ansible
    curl
    software-properties-common
)

# Check which packages are missing
MISSING_PACKAGES=()
for pkg in "${PACKAGES[@]}"; do
    if ! dpkg -s "$pkg" >/dev/null 2>&1; then
        MISSING_PACKAGES+=("$pkg")
    fi
done

if [[ ${#MISSING_PACKAGES[@]} -gt 0 ]]; then
    log_info "Installing missing packages: ${MISSING_PACKAGES[*]}"
    sudo apt install -y "${MISSING_PACKAGES[@]}"
else
    log_info "All system packages already installed."
fi

# ============================================================================
# Step 2: Git configuration
# ============================================================================
log_info "Step 2: Configuring git hooks..."

if [[ ! -f .gitconfig ]]; then
    git config -f .gitconfig core.hooksPath .githooks
fi
git config --local include.path "$(pwd)/.gitconfig"

log_info "Git hooks configured."

# ============================================================================
# Step 3: Ansible roles
# ============================================================================
log_info "Step 3: Installing Ansible Galaxy roles..."

mkdir -p ./ansible/roles

# Silence Ansible warnings
export ANSIBLE_LOCALHOST_WARNING=False
export ANSIBLE_INVENTORY_UNPARSED_WARNING=False

# Install roles if not already present
ROLES=(
    "geerlingguy.docker"
    "geerlingguy.node_exporter"
)

for role in "${ROLES[@]}"; do
    role_dir="./ansible/roles/${role##*.}"
    if [[ ! -d "$role_dir" ]] && [[ ! -d "./ansible/roles/$role" ]]; then
        log_info "Installing Ansible role: $role"
        ansible-galaxy install "$role" -p ./ansible/roles
    else
        log_info "Ansible role already installed: $role"
    fi
done

# ============================================================================
# Step 4: Docker installation
# ============================================================================
log_info "Step 4: Installing Docker..."

DOCKER_JUST_INSTALLED=false
if command -v docker >/dev/null 2>&1; then
    if docker ps >/dev/null 2>&1; then
        log_info "Docker is already installed and accessible."
    elif id -nG | grep -qw docker; then
        # User is in docker group but can't access - likely needs re-login
        log_warn "Docker is installed and you're in the docker group,"
        log_warn "but the current shell session doesn't have access yet."
        log_warn "Run 'newgrp docker' or log out and back in, then run 'make install' again."
        exit 0
    else
        # Docker installed but user not in group - run ansible to add them
        log_info "Docker is installed but user not in docker group. Running setup..."
        ansible-playbook ansible/install-docker.yml
        DOCKER_JUST_INSTALLED=true
    fi
else
    log_info "Installing Docker via Ansible..."
    ansible-playbook ansible/install-docker.yml
    DOCKER_JUST_INSTALLED=true
fi

# ============================================================================
# Step 5: Basic environment setup (without Sietch)
# ============================================================================
log_info "Step 5: Setting up basic environment..."

mkdir -p services-enabled
mkdir -p external-enabled
mkdir -p etc
mkdir -p media
mkdir -p backups

# Create services-enabled/.env from template if it doesn't exist
if [[ ! -f services-enabled/.env ]]; then
    if [[ -f services-scaffold/onramp/.env.template ]]; then
        log_info "Creating services-enabled/.env from template..."
        cp services-scaffold/onramp/.env.template services-enabled/.env
    else
        log_warn "No .env template found. Creating minimal .env..."
        touch services-enabled/.env
    fi
fi

# Create other env files from templates if missing
for env_file in .env.nfs .env.external; do
    if [[ ! -f "services-enabled/$env_file" ]] && [[ -f "services-scaffold/onramp/${env_file}.template" ]]; then
        log_info "Creating services-enabled/$env_file from template..."
        cp "services-scaffold/onramp/${env_file}.template" "services-enabled/$env_file"
    fi
done

# Copy default traefik middleware
if [[ ! -f external-enabled/middleware.yml ]] && [[ -f external-available/middleware.yml ]]; then
    log_info "Initializing external-enabled/middleware.yml..."
    cp external-available/middleware.yml external-enabled/middleware.yml
fi

# ============================================================================
# Done!
# ============================================================================
echo ""
log_info "=========================================="
log_info "Bootstrap complete!"
log_info "=========================================="

# Check if we need to handle docker group membership
if [[ "$DOCKER_JUST_INSTALLED" == "true" ]]; then
    if ! docker ps >/dev/null 2>&1; then
        echo ""
        log_warn "Docker was just installed. You need to refresh your shell session"
        log_warn "for docker group membership to take effect."
        echo ""

        # Detect VSCode remote environment
        if [[ -n "${VSCODE_IPC_HOOK_CLI:-}" ]] || [[ -n "${VSCODE_GIT_ASKPASS_NODE:-}" ]]; then
            echo "VSCode Remote detected. To refresh your session:"
            echo ""
            echo "  1. Run: make kill-code"
            echo "  2. Reconnect to this machine in VSCode"
            echo "  3. Run: make continue-install"
            echo ""
        else
            echo "Please run ONE of the following:"
            echo "  1. newgrp docker    # Refresh group in current shell, then: make continue-install"
            echo "  2. Log out and log back in, then: make continue-install"
            echo ""
        fi
        exit 0
    fi
fi
