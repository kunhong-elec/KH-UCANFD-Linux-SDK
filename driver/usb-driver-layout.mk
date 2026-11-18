# SPDX-License-Identifier: GPL-2.0
# Inspect the target kernel, including split distro header trees.
KCAN_USB_H := $(firstword $(foreach d,$(abs_srctree) $(srctree) $(KERNEL_LOCATION) $(objtree) $(CURDIR) $(dir $(KERNEL_LOCATION))source,$(wildcard $(d)/include/linux/usb.h)))
KCAN_USB_DRIVER_LAYOUT := $(shell if [ -n "$(KCAN_USB_H)" ]; then awk '\
	/^struct[[:space:]]+usb_driver[[:space:]]*[{]/ { inside=1; next } \
	inside && /^[[:space:]]*};/ { exit } \
	inside && /^[[:space:]]*struct[[:space:]]+device_driver[[:space:]]+driver[[:space:]]*;/ { print "direct"; exit } \
	inside && /^[[:space:]]*struct[[:space:]]+usbdrv_wrap[[:space:]]+drvwrap[[:space:]]*;/ { print "wrapped"; exit }' "$(KCAN_USB_H)"; fi)

ifeq ($(KCAN_USB_DRIVER_LAYOUT),direct)
ccflags-y += -DKCAN_HAS_USB_DRIVER_MEMBER
else ifeq ($(KCAN_USB_DRIVER_LAYOUT),wrapped)
ccflags-y += -DKCAN_HAS_USB_DRIVER_WRAPPER
endif
