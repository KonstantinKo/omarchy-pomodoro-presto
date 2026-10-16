import QtQuick
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "konko.presto"
  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight
  property var status: null
  property string errorText: ""
  property var pendingActions: []
  readonly property bool opened: status ? status.windowVisible === true : false
  readonly property real openPanelIndicatorWidth: button.labelWidth
  onOpenedChanged: {
    if (!bar) return
    if (opened) bar.requestPopout(root)
    else if (bar.activePopout === root) bar.releasePopout(root)
  }
  readonly property string executable: Quickshell.env("HOME") + "/.local/bin/presto"

  function open() { send("open") }
  function close() { send("hide") }
  function toggle() { send("toggle") }
  function refresh() { if (!request.running) send("status") }
  function send(action) {
    if (request.running) {
      if (action !== "status") pendingActions.push(action)
      return
    }
    request.command = [executable, "--omarchy-control", action]
    request.running = true
  }

  StatusLabel {
    id: presentation
    visible: false
    status: root.status
    errorText: root.errorText
    vertical: root.vertical
  }

  Process {
    id: request
    stdout: StdioCollector {
      onStreamFinished: {
        try {
          var reply = JSON.parse(text)
          if (reply.error) { root.status = null; root.errorText = reply.error }
          else { root.status = reply; root.errorText = "" }
        } catch (error) { root.status = null; root.errorText = "Unable to read the Presto runtime" }
      }
    }
    onExited: function(code, exitStatus) {
      if (code !== 0 && !root.errorText) {
        root.status = null
        root.errorText = "Start presto-omarchy.service to reconnect"
      }
      if (root.pendingActions.length) {
        var action = root.pendingActions.shift()
        Qt.callLater(function() { root.send(action) })
      }
    }
  }
  Timer { interval: 1000; running: true; repeat: true; triggeredOnStart: true; onTriggered: root.refresh() }
  IpcHandler {
    target: "konko.presto"
    function open(): void { root.open() }
    function close(): void { root.close() }
    function toggle(): void { root.toggle() }
    function toggleTimer(): void { root.send("start-stop") }
    function reset(): void { root.send("reset") }
  }
  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: presentation.text
    tooltipText: presentation.tooltipText
    active: root.status ? root.status.isRunning : false
    activeColor: Color.accent
    onPressed: function(b) {
      if (b === Qt.RightButton) root.send("start-stop")
      else if (b === Qt.MiddleButton) root.close()
      else root.toggle()
    }
  }
}
