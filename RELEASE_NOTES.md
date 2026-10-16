Presto for Omarchy 2.2.0 opens the complete original Presto app directly from the bar.
The Omarchy theme is a regular choice alongside Espresso, Pommodore64 and PipBoy,
and is the default on Omarchy when no explicit choice is saved.

This first public plugin release includes:

- Quickshell bar controls using the actual Presto timer and history.
- The matching Linux x86_64 native runtime, exact source snapshot and SHA-256 checksums.
- An explicit runtime installer with backups and active-session protection.
- Installation, update and removal instructions; original BSL 1.1 license retained.

Install the plugin with:

```sh
omarchy plugin add https://github.com/KonstantinKo/omarchy-presto.git --enable
```

Then follow README.md to install the matching native runtime. Adding/enabling the
plugin does not automatically download or install it. No lite panel is included.

Verified on Omarchy 4.0.4 / Arch Linux. Other CPU architectures and portable Linux
binaries are not included. The original macOS-only idle monitoring remains unchanged.
