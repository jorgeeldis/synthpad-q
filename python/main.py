from arduino.app_bricks.sound_generator import (
    SoundGenerator,
    SoundEffect,
)

from arduino.app_bricks.web_ui import WebUI

from arduino.app_utils import *

ui = WebUI()

bpmValue = 100

timesignatureValue = (4, 4)

octavesValue = 8

waveformValue = "sine"

volumeValue = 1.0

attackValue = 0.01

releaseValue = 0.03

glideValue = 0.02

selectedEffect = "none"

connected = False

def build_effects():

    effects = []

    effects.append(
        SoundEffect.adsr(
            attack=attackValue,
            release=releaseValue,
        )
    )

    if selectedEffect == "chorus":

        effects.append(
            SoundEffect.chorus()
        )


    elif selectedEffect == "tremolo":

        effects.append(
            SoundEffect.tremolo()
        )


    elif selectedEffect == "vibrato":

        effects.append(
            SoundEffect.vibrato()
        )


    elif selectedEffect == "overdrive":

        effects.append(
            SoundEffect.overdrive()
        )


    elif selectedEffect == "bitcrusher":

        effects.append(
            SoundEffect.bitcrusher()
        )


    return effects

soundeffectValue = build_effects()


player = SoundGenerator(

    bpm=bpmValue,

    time_signature=timesignatureValue,

    octaves=octavesValue,

    wave_form=waveformValue,

    master_volume=volumeValue,

    sound_effects=soundeffectValue,
)


# ==========================================
# POTENTIOMETERS FROM STM32
# ==========================================

def receive_potValues(
    potRed_value,
    potBlue_value
):

    ui.send_message(
        "message",
        {
            "potBlue": potBlue_value,
            "potRed": potRed_value,
        }
    )

    return True


Bridge.provide(
    "receive_potValues",
    receive_potValues
)


def on_connect(connection):

    global connected

    connected = True

    print(
        "WebUI connected"
    )


def on_disconnect(connection):

    global connected

    connected = False

    print(
        "WebUI disconnected"
    )


def wss_send_note(
    client,
    data
):

    note = data.get("note")


    if not note:

        print(
            "Invalid note received"
        )

        return


    print(
        f"Playing: {note}"
    )


    player.play(
        note,
        1 / 4
    )

def wss_send_settings(
    client,
    data
):

    global player

    global waveformValue
    global timesignatureValue
    global bpmValue
    global octavesValue

    global volumeValue
    global attackValue
    global releaseValue
    global glideValue

    global selectedEffect
    global soundeffectValue

    waveformValue = str(
        data.get(
            "waveform",
            waveformValue
        )
    )

    bpmValue = int(
        data.get(
            "bpm",
            bpmValue
        )
    )

    bpmValue = max(
        40,
        min(
            240,
            bpmValue
        )
    )


    octavesValue = int(
        data.get(
            "octave",
            octavesValue
        )
    )


    octavesValue = max(
        1,
        min(
            8,
            octavesValue
        )
    )

    attackValue = float(
        data.get(
            "attack",
            attackValue
        )
    )


    attackValue = max(
        0.01,
        min(
            2.0,
            attackValue
        )
    )

    volumeValue = float(
        data.get(
            "volume",
            volumeValue
        )
    )


    volumeValue = max(
        0.0,
        min(
            1.0,
            volumeValue
        )
    )


    releaseValue = float(
        data.get(
            "release",
            releaseValue
        )
    )


    releaseValue = max(
        0.01,
        min(
            2.0,
            releaseValue
        )
    )

    glideValue = float(
        data.get(
            "glide",
            glideValue
        )
    )


    glideValue = max(
        0.0,
        min(
            1.0,
            glideValue
        )
    )


    selectedEffect = str(
        data.get(
            "sound_effect",
            selectedEffect
        )
    )

    timeSignatureString = str(
        data.get(
            "time_signature",
            "4,4"
        )
    )


    try:

        numerator, denominator = (
            timeSignatureString.split(",")
        )

        timesignatureValue = (
            int(numerator),
            int(denominator)
        )


    except (ValueError, TypeError):

        print(
            "Invalid time signature:",
            timeSignatureString
        )

        timesignatureValue = (
            4,
            4
        )


    soundeffectValue = (
        build_effects()
    )

    player = SoundGenerator(

        bpm=bpmValue,

        time_signature=
            timesignatureValue,

        octaves=
            octavesValue,

        wave_form=
            waveformValue,

        master_volume=
            volumeValue,

        sound_effects=
            soundeffectValue,
    )

    print(
        "------------------------------"
    )

    print(
        "Waveform:",
        waveformValue
    )

    print(
        "Effect:",
        selectedEffect
    )

    print(
        "Time Signature:",
        timesignatureValue
    )

    print(
        "BPM:",
        bpmValue
    )

    print(
        "Octave:",
        octavesValue
    )

    print(
        "Volume:",
        volumeValue
    )

    print(
        "Attack:",
        attackValue
    )

    print(
        "Release:",
        releaseValue
    )

    print(
        "Glide:",
        glideValue,
        "(stored, not applied)"
    )

    print(
        "------------------------------"
    )

ui.on_connect(
    on_connect
)

ui.on_disconnect(
    on_disconnect
)

ui.on_message(
    "send_note",
    wss_send_note
)

ui.on_message(
    "send_settings",
    wss_send_settings
)

App.run()