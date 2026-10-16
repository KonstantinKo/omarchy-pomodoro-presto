import QtQuick
import QtTest
import ".."

TestCase {
  name: "PrestoBarPresentation"
  when: windowShown
  width: 500
  height: 100
  StatusLabel { id: label; anchors.centerIn: parent }
  function init() { label.status = null; label.errorText = ""; label.vertical = false }
  function test_unavailable_never_displays_a_fabricated_timer() {
    compare(label.text, "󰔟 !")
    verify(label.tooltipText.indexOf("unavailable") >= 0)
  }
  function test_booting_waits_for_real_tray_update() {
    label.status = {ready: false}
    compare(label.text, "󰔟 …")
  }
  function test_original_overtime_and_counts_are_preserved() {
    label.status = {ready: true, modeIcon: "◉", timerText: "+02:37 (4/10)", mode: "focus", isRunning: true, isPaused: false}
    compare(label.text, "◉ +02:37 (4/10)")
    verify(label.tooltipText.indexOf("running") >= 0)
  }
  function test_icon_only_is_not_duplicated() {
    label.status = {ready: true, modeIcon: "", timerText: "☾", mode: "longBreak", isRunning: false, isPaused: false}
    compare(label.text, "☾")
  }
  function test_paused_state_and_vertical_layout() {
    label.status = {ready: true, modeIcon: "⏸︎", timerText: "23:41 (0/10)", mode: "focus", isRunning: false, isPaused: true}
    verify(label.tooltipText.indexOf("paused") >= 0)
    label.vertical = true
    compare(label.text, "⏸︎")
  }
  function test_transport_error_hides_stale_countdown() {
    label.status = {ready: true, modeIcon: "◉", timerText: "23:41 (0/10)"}
    label.errorText = "Service stopped"
    compare(label.text, "󰔟 !")
    verify(label.tooltipText.indexOf("Service stopped") >= 0)
  }
}
