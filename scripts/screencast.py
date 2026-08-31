#!/usr/bin/env python3
"""GNOME の画面録画を D-Bus 経由で回す。

gdbus call だと呼び出したプロセスがすぐ終わり、GNOME が
"Sender has vanished" で録画を止めてしまう。接続を保ったまま待つ必要がある。

    python3 screencast.py <出力パス> <秒数>
"""
import sys
import time

import gi
from gi.repository import Gio, GLib

path, seconds = sys.argv[1], float(sys.argv[2])

bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
proxy = Gio.DBusProxy.new_sync(
    bus, Gio.DBusProxyFlags.NONE, None,
    "org.gnome.Shell.Screencast", "/org/gnome/Shell/Screencast",
    "org.gnome.Shell.Screencast", None)

opts = {"framerate": GLib.Variant("i", 15), "draw-cursor": GLib.Variant("b", True)}
ok, name = proxy.Screencast("(sa{sv})", path, opts)
print(f"start: ok={ok} file={name}", flush=True)
if not ok:
    sys.exit("could not start")

time.sleep(seconds)                 # ここで接続を保ったまま待つのが肝
print("stopping...", flush=True)
print("stop:", proxy.StopScreencast("()"))
