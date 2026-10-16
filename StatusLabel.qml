import QtQuick

Text {
  id: root
  property var status: null
  property string errorText: ""
  property bool vertical: false
  readonly property bool unavailable: !status || errorText !== ""
  readonly property string tooltipText: unavailable
    ? "Presto unavailable" + (errorText ? " · " + errorText : "")
    : !status.ready ? "Presto is starting"
    : "Presto · " + (status.mode === "focus" ? "Focus" : status.mode === "longBreak" ? "Long break" : "Short break")
      + " · " + (status.isRunning ? "running" : status.isPaused ? "paused" : "ready")
      + "\nLeft: Presto · Right: start/pause · Middle: hide"
  textFormat: Text.PlainText
  text: unavailable ? "󰔟 !" : !status.ready ? "󰔟 …"
    : vertical ? (status.modeIcon || status.timerText)
    : ((status.modeIcon ? status.modeIcon + " " : "") + status.timerText)
}
