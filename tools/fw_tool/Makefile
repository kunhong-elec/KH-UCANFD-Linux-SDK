# Makefile for KCAN Firmware Tool
#
# Build: make
# Clean: make clean
# Install: sudo make install

CC = gcc
CFLAGS = -Wall -Wextra -O2
LDFLAGS =

# Target
TARGET = kcan_fw_tool

# Source files
SRCS = kcan_fw_tool.c
OBJS = $(SRCS:.c=.o)

# Install directory
PREFIX ?= /usr/local
BINDIR = $(PREFIX)/bin

# Firmware upgrade script and images
FW_SCRIPT = kcan_fw_upgrade.sh
FW_PY_SCRIPT = kcan_fw_upgrade.py
FW_SCRIPT_INSTALL_NAME = kcan_fw_upgrade_bash
FW_PY_SCRIPT_INSTALL_NAME = kcan_fw_upgrade
FW_RELEASE_MODULE = kcan_firmware_release.py

.PHONY: all clean install uninstall help

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJS) $(TARGET)

install: $(TARGET)
	install -d $(DESTDIR)$(BINDIR)
	install -m 755 $(TARGET) $(DESTDIR)$(BINDIR)/
	install -m 755 $(FW_SCRIPT) $(DESTDIR)$(BINDIR)/$(FW_SCRIPT_INSTALL_NAME)
	install -m 755 $(FW_PY_SCRIPT) $(DESTDIR)$(BINDIR)/$(FW_PY_SCRIPT_INSTALL_NAME)
	install -m 644 $(FW_RELEASE_MODULE) $(DESTDIR)$(BINDIR)/

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/$(TARGET)
	rm -f $(DESTDIR)$(BINDIR)/$(FW_SCRIPT_INSTALL_NAME)
	rm -f $(DESTDIR)$(BINDIR)/$(FW_PY_SCRIPT_INSTALL_NAME)
	# Backward compatibility: remove old install names if they exist.
	rm -f $(DESTDIR)$(BINDIR)/kcan_fw_upgrade.sh
	rm -f $(DESTDIR)$(BINDIR)/kcan_fw_upgrade.py
	rm -f $(DESTDIR)$(BINDIR)/$(basename $(FW_SCRIPT))
	rm -f $(DESTDIR)$(BINDIR)/$(basename $(FW_PY_SCRIPT))
	rm -f $(DESTDIR)$(BINDIR)/$(FW_RELEASE_MODULE)

# Static build (for distribution)
static: LDFLAGS += -static
static: clean all

help:
	@echo "KCAN Firmware Tool - Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all       - Build the firmware tool (default)"
	@echo "  clean     - Remove build artifacts"
	@echo "  install   - Install to $(BINDIR)"
	@echo "  uninstall - Remove from $(BINDIR)"
	@echo "  static    - Build statically linked binary"
	@echo "  help      - Show this help"
