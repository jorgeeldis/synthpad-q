const ui = new WebUI();

const notePads = document.querySelectorAll('.note-pad');

const selectedWaveform = document.getElementById('waveform');
const selectedSoundEffect = document.getElementById('sound-effect');
const selectedTimeSignature = document.getElementById('time-signature');

const bpmButton = document.getElementById('bpmbutton');
const octaveButton = document.getElementById('octavebutton');
const attackButton = document.getElementById('attackbutton');

const bpmValueDisplay = document.getElementById('bpmvalue');
const octaveValueDisplay = document.getElementById('octavevalue');
const attackValueDisplay = document.getElementById('attackvalue');

const blueButtons = {
    bpm: bpmButton,
    octave: octaveButton,
    attack: attackButton,
};

const set = (key, value) => ui.send_message('set', { key, value });


// --- Server -> UI: Python owns the state, the UI only renders it ---
function selectBlueParameter(selectedButton) {
    Object.values(blueButtons).forEach(b => b.classList.remove('active'));
    selectedButton?.classList.add('active');
}

function renderState(s) {
    bpmValueDisplay.textContent = s.bpm;
    octaveValueDisplay.textContent = s.octave;
    attackValueDisplay.textContent = Number(s.attack).toFixed(2);

    selectedWaveform.value = s.waveform;
    selectedSoundEffect.value = s.sound_effect;
    selectedTimeSignature.value = s.time_signature;

    selectBlueParameter(blueButtons[s.blue]);
}

ui.on_message('state', renderState);
ui.on_connect(() => console.log('Connected to the server'));
ui.on_disconnect(() => console.log('Disconnected from the server'));


// --- UI -> Server: send single-key deltas only ---
selectedWaveform.addEventListener('change', e => set('waveform', e.target.value));
selectedSoundEffect.addEventListener('change', e => set('sound_effect', e.target.value));
selectedTimeSignature.addEventListener('change', e => set('time_signature', e.target.value));

Object.entries(blueButtons).forEach(([param, btn]) => {
    btn.addEventListener('click', () => set('blue', param));
});

notePads.forEach(pad => {
    pad.addEventListener('click', e => {
        const note = e.currentTarget.dataset.note;
        if (!note) {
            console.error('Note pad does not have data-note');
            return;
        }
        ui.send_message('send_note', { note });
    });
});