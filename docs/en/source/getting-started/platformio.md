# PlatformIO Setup

Sample code ships as one PlatformIO project per chapter.

```bash
uv tool install platformio        # or: pipx install platformio
pio run -d <chapter_dir> -t upload
pio device monitor -b 115200
```

## Check your setup

From `docs/os-on-arduino/code/`, flash the environment-check sketch:

```bash
pio run -d 00_intro -t upload
pio device monitor -b 115200
```

You are ready when the monitor prints `Environment OK! Ready to start.` and
`Loop count:`, and the LED matrix shows "OS".

```{figure} ../_static/uno_r4_wifi_os.jpg
:name: fig-platformio-os
:width: 80%

`00_intro` flashed: "OS" on the LED matrix
```

```{note}
The sketch waits until a serial monitor is opened on the PC before it draws
"OS". Flashing alone leaves the matrix dark, so open the serial monitor.
```
