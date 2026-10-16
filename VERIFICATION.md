# Release 2.2.0 verification

Verified locally on 2026-10-16 with Omarchy 4.0.4 / Arch Linux, x86_64.
The application source revision is `b9935f54c9d5da2e4ca842699fdea51440624668`.

| Suite | Passed |
| --- | ---: |
| Presto native workspace | 478 |
| Presto WASM bridge | 82 |
| Presto UI journeys, including original visual baselines | 26 |
| Omarchy bar behavior | 6 |
| Runtime installer and release packaging | 7 |
| **Total** | **599** |

The six QML behavior tests also execute two lifecycle hooks. These hooks are not
included in the total. No original application test or visual baseline was removed
or regenerated for publication.

Additional release checks passed:

- `omarchy plugin validate .` on the published plugin layout.
- Standard `omarchy plugin add <public-repository> --yes` in an isolated home:
  the manifest/entry points install, the lite panel is absent, and no runtime
  installer executes. Only shell IPC was stubbed to protect the live desktop.
- Real Tauri runtime smoke with isolated user data: Omarchy default selection,
  single-instance behavior, show/hide, pause/resume, hidden completion,
  original persistence, skip/abort/reset and invalid-control handling.
- Downloaded runtime and source asset checksums match `SHA256SUMS`.
- The downloaded application is byte-identical to the tested native binary.
- Shell syntax and clean tracked working tree.

Presto commands (from the extracted application source):

```sh
cargo test --workspace --frozen
CARGO_TARGET_WASM32_UNKNOWN_UNKNOWN_RUNNER=wasm-bindgen-test-runner cargo test -p presto-web --target wasm32-unknown-unknown --frozen
# Run the documented Playwright suite against the release frontend:
(cd tests/e2e && NO_COLOR=true npx playwright test --workers=1)
python3 integrations/omarchy/tests/runtime_smoke.py
```

Plugin/packaging commands are in README.md. Tests use the original browser bridge
mock where documented; they do not prove signed updater delivery, physical audio
output or macOS-only OS integration on Linux. The runtime package is a dynamically
linked Arch/Omarchy build, not a distribution-independent portable executable.
