import threading
from typing import Any

from arduino.app_bricks.sound_generator import SoundGenerator, SoundEffect
from arduino.app_bricks.web_ui import WebUI
from arduino.app_utils import *

ui = WebUI()

FX = {
    "adsr": SoundEffect.adsr,
    "chorus": SoundEffect.chorus,
    "tremolo": SoundEffect.tremolo,
    "vibrato": SoundEffect.vibrato,
    "overdrive": SoundEffect.overdrive,
    "bitcrusher": SoundEffect.bitcrusher,
}

# Parameters driven by the blue pot: (min, max)
RANGES = {
    "bpm": (40, 240),
    "octave": (1, 8),
    "attack": (0.01, 2.0),
}

# Values a client is allowed to set via "set"
VALID: dict[str, set[str]] = {
    "waveform": {"sine", "square", "triangle", "sawtooth"},
    "sound_effect": set(FX),
    "time_signature": {"4,4", "3,4", "2,4", "6,8"},
    "blue": set(RANGES),
}

DEADBAND = 4  # raw ADC counts; suppresses pot jitter at rounding boundaries
VOLUME = 1.0

lock = threading.Lock()
last_raw = -1

state: dict[str, Any] = {
    "bpm": 100,
    "octave": 8,
    "attack": 0.01,  # TODO: not applied to the generator yet
    "waveform": "sine",
    "sound_effect": "adsr",
    "time_signature": "4,4",
    "blue": "bpm",  # which parameter the blue pot controls
}


def build() -> SoundGenerator:
    """Build a generator from `state`. Call with `lock` held."""
    num, den = map(int, state["time_signature"].split(","))
    fx = FX.get(state["sound_effect"])
    return SoundGenerator(
        bpm=state["bpm"],
        time_signature=(num, den),
        octaves=state["octave"],
        wave_form=state["waveform"],
        master_volume=VOLUME,
        sound_effects=[fx()] if fx else [],
    )


player = build()


def broadcast_state(snapshot: dict[str, Any]) -> None:
    ui.send_message("state", snapshot)

def receive_potValues(potRed_value, potBlue_value):
    global player, last_raw

    raw = min(1023, max(0, int(potBlue_value)))
    if abs(raw - last_raw) < DEADBAND and raw not in (0, 1023):
        return True
    last_raw = raw

    with lock:
        key = state["blue"]
        lo, hi = RANGES[key]
        v = lo + raw * (hi - lo) / 1023
        v = round(v, 2) if key == "attack" else round(v)

        if v == state[key]:
            return True

        state[key] = v
        player = build()
        snapshot = dict(state)

    broadcast_state(snapshot)
    return True


Bridge.provide("receive_potValues", receive_potValues)


def on_connect(connection):
    print("WebUI connected")
    with lock:
        snapshot = dict(state)
    broadcast_state(snapshot)  # sync a fresh page to the real state


def on_disconnect(connection):
    print("WebUI disconnected")


def wss_set(client, data):
    """Client delta: {"key": "waveform", "value": "triangle"}"""
    global player

    key, val = data.get("key"), data.get("value")
    if key not in VALID or val not in VALID[key]:
        return  # unknown key, or pot-owned param, or bad value

    with lock:
        state[key] = val
        if key != "blue":  # blue only changes what the pot controls
            player = build()
        snapshot = dict(state)

    print(f"set {key}={val}")
    broadcast_state(snapshot)


def wss_send_note(client, data):
    p = player  # snapshot the reference; a concurrent swap can't affect this note
    note = data["note"]
    print(f"Playing: {note}")
    p.play(note, 1 / 4)

ui.on_connect(on_connect)
ui.on_disconnect(on_disconnect)
ui.on_message("set", wss_set)
ui.on_message("send_note", wss_send_note)

App.run()