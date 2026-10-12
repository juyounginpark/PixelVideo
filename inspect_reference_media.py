"""Extract reproducible visual/audio evidence from downloaded reference videos."""
from pathlib import Path
import hashlib
import json
import math
import re
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
for video in sorted((ROOT / 'references').rglob('*.mp4')):
    output = ROOT / 'research' / 'video_analysis' / video.stem
    frames = output / 'frames'
    frames.mkdir(parents=True, exist_ok=True)
    probe = subprocess.run([ffmpeg, '-hide_banner', '-i', str(video)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    (output / 'media_info.txt').write_text(probe.stderr, encoding='utf-8')
    duration_match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', probe.stderr)
    hours, minutes, seconds = map(float, duration_match.groups())
    duration = hours * 3600 + minutes * 60 + seconds
    subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(video), '-vf', 'fps=1,scale=360:640', str(frames / '%04d.jpg')], check=True)
    subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(video), '-vn', '-ac', '1', '-ar', '16000', str(output / 'audio.wav')], check=True)
    # fps=1 samples near interval midpoints; labels are nominal one-second bins.
    images = sorted(frames.glob('*.jpg'))
    indices = sorted(set(list(range(0, len(images), 3)) + [len(images)-1]))
    for start in range(0, len(indices), 12):
        batch = indices[start:start+12]
        sheet = Image.new('RGB', (1080, 664 * math.ceil(len(batch)/3)), '#151515')
        draw = ImageDraw.Draw(sheet)
        for cell, index in enumerate(batch):
            x, y = (cell % 3) * 360, (cell // 3) * 664
            sheet.paste(Image.open(images[index]), (x, y+24))
            draw.text((x+8, y+4), f'{index//60:02d}:{index%60:02d}  {video.stem}', fill='white')
        sheet.save(output / f'contact_{start//12+1:02d}.jpg', quality=93)
    scene = subprocess.run([ffmpeg, '-hide_banner', '-i', str(video), '-vf', "select='gt(scene,0.30)',showinfo", '-an', '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    candidate_times = [float(t) for t in re.findall(r'pts_time:([0-9.]+)', scene.stderr)]
    info = {'video': str(video.relative_to(ROOT)), 'sha256': hashlib.sha256(video.read_bytes()).hexdigest(),
            'duration_seconds': duration, 'frame_sampling': 'fps=1, nominal second bins, approximately +/-0.5s',
            'contact_sampling_seconds': 3, 'scene_threshold': 0.30,
            'scene_candidate_times': candidate_times,
            'audio': 'audio.wav, mono 16000 Hz, extracted from local video', 'visual_observation': 'pending'}
    (output / 'evidence.json').write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
    print(video.stem, 'duration=', duration, 'frames=', len(images), 'scene_candidates=', candidate_times, flush=True)
