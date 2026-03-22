# vibeOS Build System
# ============================================================================

.PHONY: iso clean test help

ISO_DIR := build/out
WORK_DIR := build/work

help: ## Show this help
	@echo "vibeOS Build Targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

iso: ## Build vibeOS ISO (requires root + archiso)
	sudo bash build.sh

iso-clean: ## Build clean ISO (removes previous build first)
	sudo bash build.sh --clean

clean: ## Remove build artifacts
	rm -rf $(WORK_DIR) $(ISO_DIR)

test-qemu-uefi: ## Test ISO in QEMU (UEFI mode)
	@ISO=$$(ls -t $(ISO_DIR)/vibeos-*.iso 2>/dev/null | head -1); \
	if [ -z "$$ISO" ]; then echo "No ISO found. Run 'make iso' first."; exit 1; fi; \
	echo "Booting: $$ISO"; \
	qemu-system-x86_64 \
		-cdrom "$$ISO" \
		-m 4G \
		-cpu host \
		-enable-kvm \
		-smp 4 \
		-bios /usr/share/ovmf/x64/OVMF.fd \
		-vga virtio \
		-display sdl,gl=on \
		-device virtio-net-pci,netdev=net0 \
		-netdev user,id=net0 \
		-boot d

test-qemu-bios: ## Test ISO in QEMU (BIOS mode)
	@ISO=$$(ls -t $(ISO_DIR)/vibeos-*.iso 2>/dev/null | head -1); \
	if [ -z "$$ISO" ]; then echo "No ISO found. Run 'make iso' first."; exit 1; fi; \
	echo "Booting: $$ISO"; \
	qemu-system-x86_64 \
		-cdrom "$$ISO" \
		-m 4G \
		-cpu host \
		-enable-kvm \
		-smp 4 \
		-vga virtio \
		-display sdl \
		-device virtio-net-pci,netdev=net0 \
		-netdev user,id=net0 \
		-boot d

test-qemu-disk: ## Test ISO in QEMU with a virtual disk for install testing
	@ISO=$$(ls -t $(ISO_DIR)/vibeos-*.iso 2>/dev/null | head -1); \
	if [ -z "$$ISO" ]; then echo "No ISO found. Run 'make iso' first."; exit 1; fi; \
	[ -f build/test-disk.qcow2 ] || qemu-img create -f qcow2 build/test-disk.qcow2 40G; \
	echo "Booting: $$ISO (with 40G test disk)"; \
	qemu-system-x86_64 \
		-cdrom "$$ISO" \
		-hda build/test-disk.qcow2 \
		-m 4G \
		-cpu host \
		-enable-kvm \
		-smp 4 \
		-bios /usr/share/ovmf/x64/OVMF.fd \
		-vga virtio \
		-display sdl,gl=on \
		-device virtio-net-pci,netdev=net0 \
		-netdev user,id=net0 \
		-boot d

wallpaper: ## Generate default wallpaper
	bash iso-profile/airootfs/usr/share/vibeos/wallpapers/generate-default.sh
