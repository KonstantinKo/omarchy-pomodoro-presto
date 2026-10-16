# Marketplace listing draft

Submit this after the repository and release are public using:
https://github.com/omacom/omarchy-plugin-marketplace/issues/new?template=submit-plugin.yml

## Repository URL

https://github.com/KonstantinKo/omarchy-presto

## Category

Productivity

## Tags

Bar, Quickshell, Hyprland

## Maintainer notes

Presto is a Pomodoro timer whose bar widget opens the complete original Presto
application directly. It has one engine, one history and one UI, including an
Omarchy theme in its existing theme picker. There is no lite panel.

The root manifest validates with `omarchy plugin validate .`. The plugin requires
the matching modified Presto runtime. Release v2.2.0 supplies a Linux x86_64 binary,
its exact source snapshot, the original BSL 1.1 license and SHA-256 checksums.

Adding/enabling the plugin does not download or execute an installer. The user
explicitly runs the documented runtime installer. It writes only user files,
backs up prior files and refuses to interrupt running or paused sessions. No sudo
is used, no app data is deleted, and no package-owned Omarchy files are modified.
Runtime dependencies, behavior, update/removal steps and platform limitations are
documented in README.md. Existing Presto update checks remain part of the app.

## Submission checklist to review before posting

- [ ] The repository is public and contains installation and removal instructions.
- [ ] I have documented the plugin license and any external dependencies.
- [ ] I confirm that I own or have permission to submit this plugin and its preview assets.
- [ ] The plugin does not overwrite user configuration without explicit consent.
- [ ] I understand that approval is for listing and is not a security review.
