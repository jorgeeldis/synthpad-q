# SynthPad Q

A standalone touchscreen synthesizer built on the **Arduino UNO Q** with Arduino App Lab Bricks.

SynthPad Q combines a 7" touchscreen, two physical knobs, a USB speaker and a 3D-printed enclosure into a dedicated instrument that needs no computer to play. The Linux side of the UNO Q runs the Python audio engine and the touchscreen web UI; the microcontroller side reads the knobs.

<!-- Add the demo video link and a photo of the finished device here -->

## Features

- **Synth pads:** 13 touch pads (C4 to C5) played through the Sound Generator Brick
- **Wave pads:** 5 pads (G#4, A4, A#4, B4, C5) that drive a continuous tone on the Wave Generator Brick
- **Waveforms:** sine, square, triangle, sawtooth
- **Sound effects:** ADSR, chorus, tremolo, vibrato, overdrive, bitcrusher
- **Time signatures:** 4/4, 3/4, 2/4, 6/8
- **Blue knob:** BPM (40–240), octave (1–8) or volume (0.00–1.00)
- **Red knob:** attack (0.01–2.00 s), release (0.01–2.00 s) or glide (0.00–1.00 s)

Each knob controls whichever parameter is selected for it on screen.

## Hardware

- Arduino UNO Q
- 7" touchscreen
- 2 × B10K potentiometers with knobs
- USB speaker
- USB-C hub and USB 90° adapter
- 5V 3A power supply
- 3D-printed PLA enclosure with heat-set inserts

### Wiring

| Knob | Wiper pin |
| --- | --- |
| Red | A0 |
| Blue | A1 |

The outer legs of both potentiometers share the same supply and ground. The touchscreen and the USB speaker connect to the UNO Q through the USB-C hub.

## How it works

```
Touchscreen (WebUI)        Knobs (MCU sketch)
        │  WebUI messages          │  Bridge: receive_potValues
        └───────────┬──────────────┘
                    ▼
        Python app — one central state
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
 SoundGenerator           WaveGenerator
  (Synth pads)             (Wave pads)
        └───────────┬───────────┘
                    ▼   only one at a time
              USB speaker (ALSA)
```

Both audio Bricks need the same USB speaker, and ALSA only lets one of them hold it. The Python app therefore keeps a single state object and a small mode state machine (`None`, `sound`, `wave`): pressing a Synth pad or a Wave pad stops the other engine, waits for the speaker to be released, and starts the one that is needed, retrying if the device is still busy.

The two engines are updated differently:

- **Sound Generator** takes its settings when it is created, so a change marks it as outdated and it is rebuilt from the current state on the next Synth pad press.
- **Wave Generator** exposes runtime properties, so waveform, attack, release, glide and volume change live while a tone is playing.

The sketch reads both knobs as raw 0–1023 values and sends them to Python through the Bridge. Python maps each reading to the range of the selected parameter, ignores changes smaller than 4 counts to filter out noise, and broadcasts the full state to the UI after every change. The UI keeps no state of its own; it only renders what Python sends.

## Project structure

```
synthpad-q/
├── app.yaml            App Lab app definition (WebUI, Sound Generator, Wave Generator Bricks)
├── python/main.py      Backend: state, mode switching, knob mapping, WebUI handlers
├── sketch/sketch.ino   MCU sketch: reads the knobs and calls receive_potValues
└── assets/             Touchscreen UI (index.html, style.css, app.js)
```

## Running it

1. Wire the knobs and connect the touchscreen and USB speaker as described above.
2. Copy this folder into your apps in Arduino App Lab on the UNO Q.
3. Open **synthpad-q** in App Lab and run it. App Lab uploads the sketch and starts the Python app.
4. Open the app's web UI on the touchscreen and play.

## Author

[jorgeeldis](https://github.com/jorgeeldis)
