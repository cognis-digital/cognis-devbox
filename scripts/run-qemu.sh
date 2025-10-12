#!/usr/bin/env bash
# Boot the built image under KVM/QEMU.
set -euo pipefail
qemu-system-x86_64 -enable-kvm -m 8192 -smp 4 \
  -drive file=output-devbox/cognis-devbox.qcow2,if=virtio \
  -net nic -net user,hostfwd=tcp::2222-:22 -nographic
