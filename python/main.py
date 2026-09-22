import threading
import time
from typing import Any

from arduino.app_bricks.sound_generator import SoundGenerator, SoundEffect
from arduino.app_bricks.wave_generator import WaveGenerator
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

BLUE_RANGES = {
    "bpm": (40, 240),
    "octave": (1, 8),
    "volume": (0.0, 1.0),
}

RED_RANGES = {
    "attack": (0.01, 2.0),
    "release": (0.01, 2.0),
    "glide": (0.0, 1.0),
}

DECIMALS = {
    "bpm": 0,
    "octave": 0,
    "volume": 2,
    "attack": 2,
    "release": 2,
    "glide": 2,
}

VALID = {
    "waveform": {"sine", "square", "triangle", "sawtooth"},
    "sound_effect": set(FX),
    "time_signature": {"4,4", "3,4", "2,4", "6,8"},
    "blue": set(BLUE_RANGES),
    "red": set(RED_RANGES),
}

DEADBAND = 4

SOUND_KEYS = {
    "bpm",
    "octave",
    "volume",
    "waveform",
    "sound_effect",
    "time_signature",
}

WAVE_KEYS = {
    "waveform",
    "volume",
    "attack",
    "release",
    "glide",
}

lock = threading.Lock()

last_raw_blue = -1
last_raw_red = -1

state: dict[str, Any] = {
    "bpm": 100,
    "octave": 8,
    "volume": 1.0,
    "attack": 0.01,
    "release": 0.03,
    "glide": 0.02,
    "waveform": "sine",
    "sound_effect": "adsr",
    "time_signature": "4,4",
    "blue": "bpm",
    "red": "attack",
}

mode = None

player: SoundGenerator | None = None
wave_gen: WaveGenerator | None = None

sound_dirty = True

WAVE_AMPLITUDE = 0.7

START_RETRY_ATTEMPTS = 4
START_RETRY_DELAY = 0.1

NOTE_FREQUENCIES = {
    "C4": 261.63,
    "C#4": 277.18,
    "D4": 293.66,
    "D#4": 311.13,
}


def build_player() -> SoundGenerator:
    numerator, denominator = map(
        int,
        state["time_signature"].split(",")
    )

    effect = FX.get(state["sound_effect"])

    return SoundGenerator(
        bpm=state["bpm"],
        time_signature=(numerator, denominator),
        octaves=state["octave"],
        wave_form=state["waveform"],
        master_volume=state["volume"],
        sound_effects=[effect()] if effect else [],
    )


def build_wave_gen() -> WaveGenerator:
    generator = WaveGenerator(
        wave_type=state["waveform"],
        attack=state["attack"],
        release=state["release"],
        glide=state["glide"],
    )

    generator.frequency = 440.0
    generator.amplitude = WAVE_AMPLITUDE
    generator.volume = int(state["volume"] * 100)

    return generator


def start_brick(brick) -> bool:
    for attempt in range(START_RETRY_ATTEMPTS):
        try:
            App.start_brick(brick)
            return True

        except Exception as exc:
            if attempt == START_RETRY_ATTEMPTS - 1:
                print(
                    f"Failed to start {type(brick).__name__}:",
                    exc
                )
                return False

            time.sleep(START_RETRY_DELAY)

    return False


def stop_sound():
    global player

    if player is not None:
        try:
            App.stop_brick(player)
        except Exception as exc:
            print("SoundGenerator stop error:", exc)

        player = None

        time.sleep(0.30)


def stop_wave():
    global wave_gen

    if wave_gen is not None:
        try:
            App.stop_brick(wave_gen)
        except Exception as exc:
            print("WaveGenerator stop error:", exc)

        wave_gen = None

        time.sleep(0.30)


def use_sound_mode():
    global mode
    global player
    global sound_dirty

    if mode == "sound" and player is not None and not sound_dirty:
        return True

    if mode == "wave":
        print("Stopping WaveGenerator...")
        stop_wave()
        mode = None

    elif mode == "sound" and player is not None:
        print("Restarting SoundGenerator...")
        stop_sound()
        mode = None

    print("Building SoundGenerator...")

    player = build_player()

    print("SoundGenerator settings:")
    print("BPM:", state["bpm"])
    print("Octave:", state["octave"])
    print("Volume:", state["volume"])
    print("Waveform:", state["waveform"])
    print("Sound Effect:", state["sound_effect"])
    print("Time Signature:", state["time_signature"])

    if not start_brick(player):
        player = None
        mode = None
        return False

    mode = "sound"
    sound_dirty = False

    print("MODE = SOUND")

    return True


def use_wave_mode():
    global mode
    global wave_gen

    if mode == "wave" and wave_gen is not None:
        return True

    if mode == "sound":
        print("Stopping SoundGenerator...")
        stop_sound()
        mode = None

    print("Building WaveGenerator...")

    wave_gen = build_wave_gen()

    print("WaveGenerator settings:")
    print("Waveform:", state["waveform"])
    print("Attack:", state["attack"])
    print("Release:", state["release"])
    print("Glide:", state["glide"])
    print("Volume:", state["volume"])

    if not start_brick(wave_gen):
        wave_gen = None
        mode = None
        return False

    wave_gen.amplitude = WAVE_AMPLITUDE
    wave_gen.volume = int(state["volume"] * 100)

    mode = "wave"

    print("MODE = WAVE")

    return True


def update_wave_generator(key):
    if wave_gen is None:
        return

    if key == "waveform":
        wave_gen.wave_type = state["waveform"]

    elif key == "volume":
        wave_gen.volume = int(state["volume"] * 100)

    elif key == "attack":
        wave_gen.attack = state["attack"]

    elif key == "release":
        wave_gen.release = state["release"]

    elif key == "glide":
        wave_gen.glide = state["glide"]


def update_settings(key):
    global sound_dirty

    if key in SOUND_KEYS:
        sound_dirty = True

    if mode == "wave" and key in WAVE_KEYS:
        update_wave_generator(key)


def broadcast_state(snapshot):
    ui.send_message(
        "state",
        dict(
            snapshot,
            mode=mode
        )
    )


def receive_potValues(potRed_value, potBlue_value):
    global last_raw_blue
    global last_raw_red

    with lock:

        changed = []

        raw_blue = min(
            1023,
            max(0, int(potBlue_value))
        )

        if (
            abs(raw_blue - last_raw_blue) >= DEADBAND
            or raw_blue in (0, 1023)
        ):
            last_raw_blue = raw_blue

            key = state["blue"]

            lo, hi = BLUE_RANGES[key]

            value = round(
                lo + raw_blue * (hi - lo) / 1023,
                DECIMALS[key]
            )

            if value != state[key]:
                state[key] = value
                changed.append(key)

        raw_red = min(
            1023,
            max(0, int(potRed_value))
        )

        if (
            abs(raw_red - last_raw_red) >= DEADBAND
            or raw_red in (0, 1023)
        ):
            last_raw_red = raw_red

            key = state["red"]

            lo, hi = RED_RANGES[key]

            value = round(
                lo + raw_red * (hi - lo) / 1023,
                DECIMALS[key]
            )

            if value != state[key]:
                state[key] = value
                changed.append(key)

        if not changed:
            return True

        for key in changed:
            update_settings(key)

        snapshot = dict(state)

    broadcast_state(snapshot)

    return True


Bridge.provide(
    "receive_potValues",
    receive_potValues
)


def on_connect(connection):
    print("WebUI connected")

    with lock:
        snapshot = dict(state)

    broadcast_state(snapshot)


def on_disconnect(connection):
    print("WebUI disconnected")


def wss_set(client, data):
    key = data.get("key")
    value = data.get("value")

    if key not in VALID:
        return

    if value not in VALID[key]:
        return

    with lock:
        state[key] = value

        update_settings(key)

        snapshot = dict(state)

    print(
        f"Setting changed: {key} = {value}"
    )

    broadcast_state(snapshot)


def wss_send_note(client, data):
    global player

    note = data.get("note")

    if note is None:
        print("Missing note")
        return

    with lock:
        if not use_sound_mode():
            print("Could not start SoundGenerator")
            return

        p = player

    print(
        f"SoundGenerator: {note}"
    )

    p.play(
        note,
        1 / 4
    )


def wss_send_wave(client, data):
    note = data.get("note")

    if note is not None:
        frequency = NOTE_FREQUENCIES.get(note)

        if frequency is None:
            print(
                f"Unknown note: {note}"
            )
            return

    else:
        try:
            frequency = float(
                data.get("wave")
            )
        except (TypeError, ValueError):
            print(
                "Invalid wave:",
                data
            )
            return

    with lock:
        if not use_wave_mode():
            print("Could not start WaveGenerator")
            return

        wg = wave_gen

        if wg is None:
            return

        wg.frequency = frequency
        wg.amplitude = WAVE_AMPLITUDE
        wg.volume = int(
            state["volume"] * 100
        )

    print(
        f"WaveGenerator: "
        f"{frequency} Hz | "
        f"waveform={state['waveform']} | "
        f"amplitude={wg.amplitude} | "
        f"volume={wg.volume}"
    )


ui.on_connect(
    on_connect
)

ui.on_disconnect(
    on_disconnect
)

ui.on_message(
    "set",
    wss_set
)

ui.on_message(
    "send_note",
    wss_send_note
)

ui.on_message(
    "send_wave",
    wss_send_wave
)

App.run()