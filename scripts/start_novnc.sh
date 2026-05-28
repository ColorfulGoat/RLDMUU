#!/usr/bin/env bash
set -e

if [ "${ENABLE_NOVNC:-1}" = "1" ]; then
    export DISPLAY=${DISPLAY:-:1}
    export RESOLUTION=${RESOLUTION:-1280x720x24}
    export VNC_PORT=${VNC_PORT:-5901}
    export NOVNC_PORT=${NOVNC_PORT:-6080}

    Xvfb "$DISPLAY" -screen 0 "$RESOLUTION" &
    sleep 2

    dbus-launch --exit-with-session startxfce4 >/tmp/xfce.log 2>&1 &

    x11vnc \
      -display "$DISPLAY" \
      -forever \
      -shared \
      -nopw \
      -rfbport "$VNC_PORT" \
      >/tmp/x11vnc.log 2>&1 &

    websockify \
      --web=/usr/share/novnc \
      "$NOVNC_PORT" \
      "localhost:$VNC_PORT" \
      >/tmp/novnc.log 2>&1 &

    echo "noVNC running at: http://localhost:${NOVNC_PORT}/vnc.html"
else
    echo "noVNC disabled. Running in headless mode."
fi

echo "Workspace: /workspace"

exec "$@"
