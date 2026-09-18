const ui = new WebUI();

const notePads = document.querySelectorAll('.note-pad');


// Synth settings
const selectedWaveform =
  document.getElementById('waveform');

const selectedSoundEffect =
  document.getElementById('sound-effect');

const selectedTimeSignature =
  document.getElementById('time-signature');


const bpmButton =
  document.getElementById('bpmbutton');

const octaveButton =
  document.getElementById('octavebutton');

const attackButton =
  document.getElementById('attackbutton');


const bpmValueDisplay =
  document.getElementById('bpmvalue');

const octaveValueDisplay =
  document.getElementById('octavevalue');

const attackValueDisplay =
  document.getElementById('attackvalue');

const volumeButton =
  document.getElementById('volumebutton');

const releaseButton =
  document.getElementById('releasebutton');

const glideButton =
  document.getElementById('glidebutton');


const volumeValueDisplay =
  document.getElementById('volumevalue');

const releaseValueDisplay =
  document.getElementById('releasevalue');

const glideValueDisplay =
  document.getElementById('glidevalue');

let mappedBPM = 100;
let mappedOctave = 8;
let mappedAttack = 0.01;

let mappedVolume = 1.0;
let mappedRelease = 0.03;
let mappedGlide = 0.02;

ui.on_connect(onUIConnected);
ui.on_disconnect(onUIDisconnected);

ui.on_message(
  'message',
  receivePotentiometers
);

selectedWaveform.addEventListener(
  'change',
  sendSettings
);

selectedSoundEffect.addEventListener(
  'change',
  sendSettings
);

selectedTimeSignature.addEventListener(
  'change',
  sendSettings
);

function selectBlueParameter(selectedButton) {

  bpmButton.classList.remove('active');
  octaveButton.classList.remove('active');
  attackButton.classList.remove('active');

  selectedButton.classList.add('active');
}


bpmButton.addEventListener('click', () => {

  selectBlueParameter(bpmButton);

});


octaveButton.addEventListener('click', () => {

  selectBlueParameter(octaveButton);

});


attackButton.addEventListener('click', () => {

  selectBlueParameter(attackButton);

});


function selectRedParameter(selectedButton) {

  volumeButton.classList.remove('active');
  releaseButton.classList.remove('active');
  glideButton.classList.remove('active');

  selectedButton.classList.add('active');
}


volumeButton.addEventListener('click', () => {

  selectRedParameter(volumeButton);

});


releaseButton.addEventListener('click', () => {

  selectRedParameter(releaseButton);

});


glideButton.addEventListener('click', () => {

  selectRedParameter(glideButton);

});

function mapRange(
  value,
  fromLow,
  fromHigh,
  toLow,
  toHigh
) {

  return (
    ((value - fromLow) *
      (toHigh - toLow)) /
    (fromHigh - fromLow)
  ) + toLow;
}

function receivePotentiometers(message) {

  const potBlue =
    Number(message.potBlue);

  const potRed =
    Number(message.potRed);

  if (
    !Number.isFinite(potBlue) ||
    !Number.isFinite(potRed)
  ) {

    console.error(
      'Invalid potentiometer data:',
      message
    );

    return;
  }

  const safePotBlue =
    Math.min(
      1023,
      Math.max(0, potBlue)
    );

  const safePotRed =
    Math.min(
      1023,
      Math.max(0, potRed)
    );


  let valueChanged = false;


  // BPM
  if (
    bpmButton.classList.contains('active')
  ) {

    const newBPM = Math.round(
      mapRange(
        safePotBlue,
        0,
        1023,
        40,
        240
      )
    );


    if (newBPM !== mappedBPM) {

      mappedBPM = newBPM;

      bpmValueDisplay.textContent =
        mappedBPM;

      valueChanged = true;
    }
  }


  // OCTAVE
  else if (
    octaveButton.classList.contains('active')
  ) {

    const newOctave = Math.round(
      mapRange(
        safePotBlue,
        0,
        1023,
        1,
        8
      )
    );


    if (newOctave !== mappedOctave) {

      mappedOctave = newOctave;

      octaveValueDisplay.textContent =
        mappedOctave;

      valueChanged = true;
    }
  }


  // ATTACK
  else if (
    attackButton.classList.contains('active')
  ) {

    const newAttack = Number(
      mapRange(
        safePotBlue,
        0,
        1023,
        0.01,
        2.0
      ).toFixed(2)
    );


    if (newAttack !== mappedAttack) {

      mappedAttack = newAttack;

      attackValueDisplay.textContent =
        mappedAttack.toFixed(2);

      valueChanged = true;
    }
  }



  // VOLUME
  if (
    volumeButton.classList.contains('active')
  ) {

    const newVolume = Number(
      mapRange(
        safePotRed,
        0,
        1023,
        0.0,
        1.0
      ).toFixed(2)
    );


    if (newVolume !== mappedVolume) {

      mappedVolume = newVolume;

      volumeValueDisplay.textContent =
        mappedVolume.toFixed(2);

      valueChanged = true;
    }
  }


  // RELEASE
  else if (
    releaseButton.classList.contains('active')
  ) {

    const newRelease = Number(
      mapRange(
        safePotRed,
        0,
        1023,
        0.01,
        2.0
      ).toFixed(2)
    );


    if (newRelease !== mappedRelease) {

      mappedRelease = newRelease;

      releaseValueDisplay.textContent =
        mappedRelease.toFixed(2);

      valueChanged = true;
    }
  }


  // GLIDE
  else if (
    glideButton.classList.contains('active')
  ) {

    const newGlide = Number(
      mapRange(
        safePotRed,
        0,
        1023,
        0.0,
        1.0
      ).toFixed(2)
    );


    if (newGlide !== mappedGlide) {

      mappedGlide = newGlide;

      glideValueDisplay.textContent =
        mappedGlide.toFixed(2);

      valueChanged = true;
    }
  }

  if (valueChanged) {
    sendSettings();
  }
}


function sendSettings() {

  const settings = {

    waveform:
      selectedWaveform.value,

    sound_effect:
      selectedSoundEffect.value,

    time_signature:
      selectedTimeSignature.value,

    bpm:
      mappedBPM,

    octave:
      mappedOctave,

    attack:
      mappedAttack,

    volume:
      mappedVolume,

    release:
      mappedRelease,

    glide:
      mappedGlide
  };


  ui.send_message(
    'send_settings',
    settings
  );


  console.log(
    'Settings sent:',
    settings
  );
}


function onUIConnected() {

  console.log(
    'Connected to the server'
  );
}


function onUIDisconnected() {

  console.log(
    'Disconnected from the server'
  );
}


notePads.forEach(pad => {

  pad.addEventListener(
    'click',
    sendNote
  );

});


function sendNote(event) {

  const note =
    event.currentTarget.dataset.note;


  if (!note) {

    console.error(
      'Note pad does not contain data-note'
    );

    return;
  }


  ui.send_message(
    'send_note',
    {
      note: note
    }
  );


  console.log(
    `Note sent: ${note}`
  );
}