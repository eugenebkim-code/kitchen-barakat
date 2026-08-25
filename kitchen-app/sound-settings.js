const fs = require('fs');
const path = require('path');
const { app, dialog } = require('electron');
const { pathToFileURL } = require('url');

const PRESETS = [
  { id: 'voice', label: 'Голос: «У вас новый заказ»', file: 'sound/preset-voice.wav' },
  { id: 'bell', label: 'Колокольчик', file: 'sound/preset-bell.wav' },
  { id: 'siren', label: 'Сирена', file: 'sound/preset-siren.wav' },
];

function settingsFilePath() {
  return path.join(app.getPath('userData'), 'sound-settings.json');
}

function customSoundPath(fileName) {
  return path.join(app.getPath('userData'), fileName);
}

function readRawSettings() {
  try {
    return JSON.parse(fs.readFileSync(settingsFilePath(), 'utf-8'));
  } catch {
    return { selected: 'voice', customFileName: null };
  }
}

function writeRawSettings(settings) {
  fs.mkdirSync(app.getPath('userData'), { recursive: true });
  fs.writeFileSync(settingsFilePath(), JSON.stringify(settings, null, 2), 'utf-8');
}

function getResolvedSettings() {
  const raw = readRawSettings();

  if (raw.selected === 'custom' && raw.customFileName) {
    const p = customSoundPath(raw.customFileName);
    if (fs.existsSync(p)) {
      return {
        presets: PRESETS,
        selected: 'custom',
        activeFile: pathToFileURL(p).href,
        customFileName: raw.customFileName,
      };
    }
  }

  const preset = PRESETS.find((p) => p.id === raw.selected) || PRESETS[0];
  return { presets: PRESETS, selected: preset.id, activeFile: preset.file, customFileName: raw.customFileName || null };
}

function setSelectedPreset(id) {
  if (!PRESETS.find((p) => p.id === id)) return getResolvedSettings();
  const raw = readRawSettings();
  writeRawSettings({ selected: id, customFileName: raw.customFileName || null });
  return getResolvedSettings();
}

async function pickAndImportCustomSound(parentWindow) {
  const result = await dialog.showOpenDialog(parentWindow, {
    title: 'Выберите файл мелодии для оповещения',
    filters: [
      { name: 'Аудио (mp3, wav, ogg, m4a)', extensions: ['mp3', 'wav', 'ogg', 'm4a'] },
    ],
    properties: ['openFile'],
  });

  if (result.canceled || !result.filePaths[0]) {
    return null;
  }

  const sourcePath = result.filePaths[0];
  const ext = path.extname(sourcePath) || '.mp3';
  const fileName = 'custom-sound' + ext;

  fs.mkdirSync(app.getPath('userData'), { recursive: true });
  fs.copyFileSync(sourcePath, customSoundPath(fileName));

  writeRawSettings({ selected: 'custom', customFileName: fileName });
  return getResolvedSettings();
}

module.exports = { PRESETS, getResolvedSettings, setSelectedPreset, pickAndImportCustomSound };
