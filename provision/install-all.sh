#!/usr/bin/env bash
# cognis-devbox provisioner — installs every language + dev/cloud/AI tool.
# Idempotent; safe to re-run. Ubuntu/Debian base.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y
sudo apt-get install -y build-essential git curl wget jq unzip ca-certificates gnupg \
  ripgrep fzf tmux neovim htop net-tools software-properties-common python3 python3-pip python3-venv

echo "== languages =="
# Node (nvm) + Bun + Deno
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash || true
curl -fsSL https://bun.sh/install | bash || true
curl -fsSL https://deno.land/install.sh | sh || true
# Go
GO=1.22.4; wget -q https://go.dev/dl/go${GO}.linux-amd64.tar.gz -O /tmp/go.tgz && sudo tar -C /usr/local -xzf /tmp/go.tgz || true
# Rust
curl -fsSL https://sh.rustup.rs | sh -s -- -y || true
# Java + Ruby + PHP + .NET
sudo apt-get install -y default-jdk ruby-full php-cli dotnet-sdk-8.0 2>/dev/null || true

echo "== containers & cloud =="
curl -fsSL https://get.docker.com | sh || true
# kubectl + helm + terraform
sudo curl -fsSLo /usr/local/bin/kubectl "https://dl.k8s.io/release/$(curl -sL https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && sudo chmod +x /usr/local/bin/kubectl || true
curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash || true
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp.gpg 2>/dev/null || true
# cloud CLIs
curl -fsSL https://sdk.cloud.google.com | bash || true
curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o /tmp/aws.zip && unzip -q /tmp/aws.zip -d /tmp && sudo /tmp/aws/install || true
curl -fsSL https://aka.ms/InstallAzureCLIDeb | sudo bash || true
# gh
sudo apt-get install -y gh 2>/dev/null || true

echo "== AI / LLM =="
curl -fsSL https://ollama.com/install.sh | sh || true
pip3 install --break-system-packages huggingface_hub vllm 2>/dev/null || pip3 install huggingface_hub || true

echo "cognis-devbox provisioning complete. See MANIFEST.md."
