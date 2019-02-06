const fs = require('fs');
const path = require('path');
const childProcess = require('child_process');
const mktemp = require('mktemp');

const express = require('express');
const app = express();

const chunkPrefix = 'live_0';
const headerFile = `${chunkPrefix}.hdr`;

const getChunkNumber = (file) => {
  return +(file.match(/(\d+).chk/) || [])[1];
};

process.chdir(process.env.TMPDIR);

const recordingDirectory = mktemp.createDirSync('letmeinsight-XXX');

process.chdir(recordingDirectory);

const ENCODER_PARAMS = [
  '-speed', 6,
  '-tile-columns', 4,
  '-frame-parallel', 1,
  '-threads', 8,
  '-static-thresh', 0,
  '-max-intra-rate', 300,
  '-deadline', 'realtime',
  '-lag-in-frames', 0,
  '-error-resilient', 1
];

console.log('Starting video chunk generator in', recordingDirectory);

const recordingProcess = childProcess.spawn('ffmpeg', [
  '-pix_fmt', 'uyvy422',
  '-f', 'avfoundation',
  '-r', 10,
  '-s', '640x480',
  '-i', 'default',
  '-map', '0:0',
  '-c:v', 'libvpx-vp9',
  '-s', '640x480',
  '-keyint_min', 10,
  '-g', 10,
  ...ENCODER_PARAMS,
  '-b:v', '300k',
  '-f', 'webm_chunk',
  '-header', 'live_0.hdr',
  '-chunk_start_index', 0,
  '-audio_chunk_duration', 1000,
  'live_0_%d.chk'
]);

process.on('SIGINT', function() {
  recordingProcess.kill('SIGINT');

  const rimraf = require('rimraf');

  console.log('Cleaning up...');
  rimraf.sync(recordingDirectory);
  console.log('Cleanup complete');

  process.exit();
});

setTimeout(() => {
  console.log('Generating stream manifest');

  childProcess.spawn('ffmpeg', [
    '-f', 'webm_dash_manifest',
    '-live', 1,
    '-i', headerFile,
    '-c', 'copy',
    '-map', 0,
    '-f', 'webm_dash_manifest',
    '-live', 1,
    '-adaptation_sets', 'id=0,streams=0',
    '-chunk_start_index', 0,
    '-chunk_duration_ms', 1000,
    '-time_shift_buffer_depth', 3000,
    '-minimum_update_period', 1,
    '-y', 'live.mpd'
  ]).on('exit', () => {
    console.log(fs.readFileSync('live.mpd', 'utf-8'));
  });
}, 3000);

const getChunkFiles = () => {
  return fs.readdirSync('.')
    .filter((file) => !isNaN(getChunkNumber(file)))
    .sort((fileA, fileB) => getChunkNumber(fileA) - getChunkNumber(fileB));
}

const lastNChunks = (n) => {
  const chunkFiles = getChunkFiles();

  return [
    headerFile,
    ...chunkFiles.slice(chunkFiles.length - 1 - n, chunkFiles.length - 1)
  ];
};

app.get('/', async (req, res) => {
  const rewindChunkFiles = lastNChunks(10);

  console.log(rewindChunkFiles);

  res.header('Content-Type', 'video/webm');

  const allExist = rewindChunkFiles.every((file) => fs.existsSync(file));

  if (!allExist) {
    return res.send(404);
  }

  for (const file of rewindChunkFiles) {
    res.write(fs.readFileSync(file));
  }

  res.end();
});

app.get('/snapshot', (req, res) => {
  res.header('Content-Type', 'image/jpeg');

  const process = childProcess.spawn('ffmpeg', [
    '-i', `concat:${lastNChunks(1).join('|')}`,
    '-frames', 1,
    '-f', 'image2',
    '-'
  ]);

  process.stdout.on('data', (data) => res.write(data));
  process.on('exit', () => res.end());
});

app.listen(9001);
