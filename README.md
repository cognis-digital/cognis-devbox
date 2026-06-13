<div align="center">

# cognis-devbox

### A custom dev OS image with *every* language + cloud + AI tool preinstalled — build once (Packer/KVM), boot anywhere.

[![License: COCL 1.0](https://img.shields.io/badge/License-COCL%201.0-2b6cb0.svg)](LICENSE) ![KVM](https://img.shields.io/badge/KVM%2FQEMU-ready-cc0000) ![Vagrant](https://img.shields.io/badge/Vagrant-libvirt%2Fvbox-1563FF?logo=vagrant) [![Suite](https://img.shields.io/badge/Cognis-Neural%20Suite-6b46c1.svg)](https://github.com/cognis-digital/cognis-neural-suite)

</div>

Stop yak-shaving a new machine. `cognis-devbox` bakes a complete polyglot dev environment into a
reusable image — see **[MANIFEST.md](MANIFEST.md)** for the full toolset.

```bash
# Option A — KVM/QEMU image (qcow2)
packer init . && packer build .          # -> output-devbox/cognis-devbox.qcow2
bash scripts/run-qemu.sh

# Option B — Vagrant (libvirt or VirtualBox)
vagrant up

# Option C — provision an existing box / cloud VM
bash provision/install-all.sh            # or use cloud-init/user-data.yaml
```

Just want the installer menu instead of a whole image? See **[omni-install](https://github.com/cognis-digital/omni-install)**.

## Usage — step by step

1. **Get the repo** — clone it and review the toolset before building:
   ```bash
   git clone https://github.com/cognis-digital/cognis-devbox && cd cognis-devbox
   ```
   See [`MANIFEST.md`](MANIFEST.md) for the full preinstalled toolset.
2. **Build the image** (KVM/QEMU qcow2) with Packer:
   ```bash
   packer init . && packer build .     # -> output-devbox/cognis-devbox.qcow2
   ```
3. **Boot it** — run the qcow2 locally, or bring it up via Vagrant:
   ```bash
   bash scripts/run-qemu.sh            # KVM/QEMU
   vagrant up                          # libvirt or VirtualBox
   ```
4. **Or provision an existing box / cloud VM** instead of building an image:
   ```bash
   bash provision/install-all.sh       # or use cloud-init/user-data.yaml
   ```
5. **Use in CI / cloud** — point `cloud-init`'s `user-data.yaml` at a fresh VM so every runner boots the same polyglot environment. Just want the installer menu? See [omni-install](https://github.com/cognis-digital/omni-install).

## How it fits

```mermaid
flowchart LR
  U[You / CI / Agent] --> R[cognis-devbox]
  R --> O[Outputs & artifacts]
  R --> M[MCP / JSON]
  M --> AI[AI agents]
  R --> S[Cognis Neural Suite]
```

**Explore the suite →** [🗂️ all tools](https://github.com/cognis-digital/cognis-neural-suite) · [⭐ awesome-cognis](https://github.com/cognis-digital/awesome-cognis) · [🔗 cognis-sources](https://github.com/cognis-digital/cognis-sources)

## License
COCL v1.0 — see [LICENSE](LICENSE).
