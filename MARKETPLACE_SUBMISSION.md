# Marketplace submission

Submitted on 2026-10-16: https://github.com/omacom/omarchy-plugin-marketplace/issues/11793

Awaiting marketplace review. The repository and v2.2.0 release are public.

## Repository URL

https://github.com/KonstantinKo/omarchy-pomodoro-presto

## Category

Productivity

## Tags

Bar, Quickshell, Hyprland

## Suggest a missing tag

Pomodoro

## Maintainer notes

Pomodoro Presto is a Pomodoro focus timer whose bar widget opens the complete
original Presto application directly. It has one engine, one history and one UI, including an
Omarchy theme in its existing theme picker. There is no lite panel.

Pomodoro Technique, configurable focus sessions, short and long breaks, work/break
intervals and timeboxing are supported. Continuous sessions let the countdown
continue in overtime for flowtime-style focus until you finish manually; break
durations stay configurable rather than being calculated from a Flowtime formula.
Tasks, tags, distraction tracking, session history, focus statistics, ambient audio
and notifications support deep work, study sessions, concentration, productivity
and personal time tracking.

Search keywords: pomodoro, pomodoro timer, focus timer, flowtime, flowtime-style
focus, deep work, timeboxing, work/break timer, break reminder, study timer,
time tracking, session history, productivity, Quickshell, Hyprland, Omarchy.

The root manifest validates with `omarchy plugin validate .`. The plugin requires
the matching modified Presto runtime. Release v2.2.0 supplies a Linux x86_64 binary,
its exact source snapshot, the original BSL 1.1 license and SHA-256 checksums.

Adding/enabling the plugin does not download or execute an installer. The user
explicitly runs the documented runtime installer. It writes only user files,
backs up prior files and refuses to interrupt running or paused sessions. No sudo
is used, no app data is deleted, and no package-owned Omarchy files are modified.
Runtime dependencies, behavior, update/removal steps and platform limitations are
documented in README.md. Existing Presto update checks remain part of the app.

## Submitted checklist

- [x] The repository is public and contains installation and removal instructions.
- [x] I have documented the plugin license and any external dependencies.
- [x] I confirm that I own or have permission to submit this plugin and its preview assets.
- [x] The plugin does not overwrite user configuration without explicit consent.
- [x] I understand that approval is for listing and is not a security review.
