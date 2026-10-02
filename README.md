# SynthPad 1986: Synthesizer Made with Arduino UNO Q

[![SynthPad 1986 demo video](https://img.youtube.com/vi/CJGNXiqGhB0/hqdefault.jpg)](https://www.youtube.com/watch?v=CJGNXiqGhB0)

**Demo video:** [Watch on YouTube](https://www.youtube.com/watch?v=CJGNXiqGhB0)

## Abstract

SynthPad 1986 is a compact and powerful digital synthesizer built around the Arduino UNO Q and developed using Bricks in Arduino App Lab. The instrument offers many functions, from changing the waveform to make the music sound futuristic or classical, to changing the beats per minute (BPM) to make it faster or slower.

The purpose of this project is to show how powerful the Arduino UNO Q can be in a practical and creative way. With the Arduino UNO Q at its core, a touchscreen, physical knobs, a speaker and a custom 3D-printed enclosure, SynthPad 1986 turns accessible hardware into a standalone platform for creating music.

In a world where more things can be made instead of bought, this project shows how you can build a quality synthesizer yourself. It is meant for creative people who want to make music and keep building on their ideas. SynthPad 1986 is designed as a platform that encourages users to experiment, create and continue developing their own musical ideas.

## Detailed Information

### Materials, Tools & Software

The materials used for this project were:

- Arduino UNO Q
- 2 × B10K potentiometers with knobs
- 1 × USB 90° adapter
- USB-C hub
- USB speaker
- 7" touchscreen
- PLA filament
- Heat-set inserts and screws
- 5V 3A power brick
- Double-sided tape
- Dupont cables
- PCB board
- 18 AWG wire

The tools used for this project were:

- Screwdrivers
- Soldering iron and solder
- Scissors
- 3D printer
- Cutting pliers
- Vernier caliper and rulers
- Hot glue gun

The software used for this project was:

- Arduino App Lab
- OrcaSlicer
- Fusion 360

### Understanding the System

SynthPad 1986 uses a state-driven architecture. Arduino App Lab provides two audio Bricks, Sound Generator and Wave Generator, and both need the same USB speaker, so they cannot run at the same time. The app therefore keeps one central state and allows only one Brick to play at a time: when one starts, the other is stopped first, and vice versa.

Sound Generator plays synth notes with settings such as BPM, octave, waveform, sound effect and time signature. Wave Generator plays a continuous tone whose waveform, attack, release and glide can be changed live. There is no separate mode button: pressing a Synth pad switches to Sound Generator, and pressing a Wave pad switches to Wave Generator.

### 3D Design & Fabrication

The entire enclosure was designed in Fusion 360. I aimed for a portable design with the touchscreen at a 45° viewing angle, which is comfortable whether you are sitting down or standing up. The design is based on the real dimensions of each component, taken from their datasheets and measured with a vernier caliper and millimeter rulers.

After designing the enclosure, I prepared the model for printing in OrcaSlicer. I used tree supports in the Tree Slim style to hold up the whole structure while saving filament and print time. All other settings were left at their defaults:

- Layer height: 0.2 mm (a balance between speed and detail)
- Infill: 15% (strong enough for structural parts while saving filament)
- Supports: tree supports, Tree Slim style
- Print temperature: 210 °C for PLA (check your specific filament)
- Bed temperature: 60 °C

Then I printed the enclosure and the frames that close everything up.

### Electronics & Build

The electronics are fairly simple. First, solder both potentiometers to a PCB board so they share the same ground and the same positive supply, powered from the same pins. The remaining pin on each potentiometer, the middle one (the wiper), goes to its own analog input on the Arduino UNO Q, so each knob controls a different group of values in the software. The red knob's wiper connects to A0 and the blue knob's wiper to A1. The sketch discards the first reading of each pin and keeps a second one taken 10 ms later, because the ADC is multiplexed and the first sample after switching channels can still carry charge from the previous pin.

Once the potentiometers are soldered, you can start assembling the device:

1. Install the heat-set inserts in their holes using the soldering iron.
2. Place the USB-C hub in the middle of the enclosure.
3. Mount the Arduino UNO Q on its base and connect it to the USB-C hub.
4. Attach the speaker with double-sided tape on top of the USB-C hub, at the back, where the sound opening is.
5. Connect the touchscreen to the USB-C hub, place it in the enclosure and screw it in.
6. Insert the potentiometers into the holes in the frame, secure them with hot glue and put on the knobs.

### Firmware & Software Development (Backend)

With everything assembled, we move to the backend, where all the magic happens. As explained in Understanding the System, the backend uses a state-driven architecture.

First, the code imports the libraries the app needs. Next, it defines the dictionaries and constants used throughout the program: the sound effects (FX), the potentiometer ranges, the decimal precision for each value, the valid values for each setting, the settings each Brick uses, and the central state that holds every current value.

Then come the functions that make everything work:

- `build_player` and `build_wave_gen` create the Sound Generator and Wave Generator using the current values in the state.
- `start_brick`, `stop_sound` and `stop_wave` start and stop the Bricks. After stopping, the code waits briefly so the speaker is released, and if a start fails it retries a few times.
- `use_sound_mode` and `use_wave_mode` are where the state-driven structure takes place: before one Brick starts, the other one is stopped, so they never run at the same time.
- `update_settings` and `update_wave_generator` apply changes coming from the web UI or the potentiometers. Wave Generator settings change live while it plays. Sound Generator is marked as outdated and rebuilt with the new settings on the next note.
- `broadcast_state` sends the current state to the web UI so the screen always shows the right values.
- `receive_potValues` receives the raw readings from both potentiometers, converts them to the range of the parameter each knob controls, and ignores tiny changes caused by electrical noise.
- `wss_set` changes a setting from the web UI, while `wss_send_note` and `wss_send_wave` play the notes received from the web UI.

### Firmware & Software Development (Frontend)

The frontend is designed as a clean, single-view interface where all the pads are right in front of you, ready to play. The top row has three cards: the first two hold the settings for the Synth pads and the Wave pads, and the third holds the five Wave pads. The second row has more settings for the Synth pads, such as sound effects, waveforms and time signatures.

### Real-World Applications

This project has many real-world applications. It can be an educational project for kids learning music through electronics, or a DIY synthesizer that music producers can build and customize for themselves.

### Conclusions

This project was made to show how powerful and creative the Arduino UNO Q can be. I wanted to make something meaningful and fun that shows off the capabilities of the Arduino UNO Q.

Generative AI was used as a development assistant for debugging and for correcting spelling and grammar in the documentation.
