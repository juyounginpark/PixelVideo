"""Local automatic speech transcription; output is evidence pending verification."""
import json
from pathlib import Path
import wave
import numpy as np
from faster_whisper import WhisperModel

root = Path(__file__).resolve().parent
print('Loading multilingual small ASR model on CPU...', flush=True)
model = WhisperModel('small', device='cpu', compute_type='int8', cpu_threads=4)
for folder in sorted((root / 'research' / 'video_analysis').iterdir()):
    wav = folder / 'audio.wav'
    if not wav.exists():
        continue
    print('Transcribing', folder.name, flush=True)
    with wave.open(str(wav), 'rb') as audio:
        assert audio.getnchannels() == 1 and audio.getframerate() == 16000 and audio.getsampwidth() == 2
        waveform = np.frombuffer(audio.readframes(audio.getnframes()), dtype='<i2').astype(np.float32) / 32768.0
    segments, info = model.transcribe(waveform, language='ko', beam_size=5, vad_filter=True)
    rows = []
    for segment in segments:
        row = {'start': round(segment.start, 3), 'end': round(segment.end, 3), 'text': segment.text,
               'avg_logprob': segment.avg_logprob, 'no_speech_prob': segment.no_speech_prob}
        rows.append(row)
        print(f"{folder.name} {segment.start:.1f}-{segment.end:.1f}: {segment.text}", flush=True)
    result = {'method': 'faster-whisper small, CPU int8, Korean, beam_size=5, vad_filter=True',
              'status': 'automatic_transcription_not_manually_auditioned',
              'language': info.language, 'segments': rows}
    (folder / 'transcript_asr.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
