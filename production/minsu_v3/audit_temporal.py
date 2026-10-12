"""Inspect consecutive decoded delivery frames; expose review evidence, not aesthetic approval."""
import argparse
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw


def audit(job, video):
    spec = json.loads((job / 'spec.json').read_text('utf-8'))
    out = job / 'review'
    out.mkdir(exist_ok=True)
    width, height = 216, 384
    command = [imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(video),
               '-an', '-vf', f'scale={width}:{height}', '-f', 'rawvideo',
               '-pix_fmt', 'rgb24', '-']
    cuts = {s['startFrame'] for s in spec['shots']}
    rows, samples, boundaries = [], {}, {}
    boundary_frames = {max(0, f + d) for f in cuts for d in (-2, -1, 0, 1, 2)}
    boundary_frames.update([0, 1, spec['durationFrames'] - 2, spec['durationFrames'] - 1])
    event_frames = {max(0, min(spec['durationFrames'] - 1, e['frame'] + d))
                    for s in spec['shots'] for e in s['events'] for d in (-3, 0, 3, 9, 18)}
    previous = None
    count = 0
    with (out / 'temporal_decode.log').open('w') as log:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=log)
        try:
            while True:
                raw = process.stdout.read(width * height * 3)
                if not raw:
                    break
                if len(raw) != width * height * 3:
                    raise RuntimeError('Truncated decoded frame')
                current = np.frombuffer(raw, np.uint8).reshape(height, width, 3)
                if previous is not None:
                    delta = np.abs(current.astype(np.int16) - previous.astype(np.int16))
                    rows.append({'frame': count, 'cut': count in cuts,
                                 'meanAbsoluteDifference': round(float(delta.mean()), 5),
                                 'changedPixelFraction': round(float(np.any(delta > 3, axis=2).mean()), 6),
                                 'meanBrightnessChange': round(float(current.mean() - previous.mean()), 5)})
                if count % 10 == 0 or count in event_frames:
                    samples[count] = Image.fromarray(current.copy())
                if count in boundary_frames:
                    boundaries[count] = Image.fromarray(current.copy())
                previous = current.copy()
                count += 1
        finally:
            process.stdout.close()
        if process.wait():
            raise RuntimeError('Final video decode failed')
    if count != spec['durationFrames']:
        raise ValueError(f'Expected {spec["durationFrames"]} frames, decoded {count}')

    def sheet(frames, images, filename, columns=5):
        canvas = Image.new('RGB', (width * columns, (height + 24) * ((len(frames) + columns - 1) // columns)), '#18212a')
        draw = ImageDraw.Draw(canvas)
        for i, f in enumerate(frames):
            x, y = i % columns * width, i // columns * (height + 24)
            canvas.paste(images[f], (x, y + 24))
            draw.text((x + 6, y + 6), f'{f:03} / {f / spec["fps"]:.2f}s', fill='white')
        canvas.save(out / filename, quality=93)

    for second in range(0, int(count / spec['fps']), 5):
        selected = [f for f in sorted(samples) if f % 10 == 0 and second * spec['fps'] <= f < (second + 5) * spec['fps']]
        sheet(selected, samples, f'encoded_sequence_{second:02}.jpg')
    for shot in spec['shots']:
        for event in shot['events']:
            selected = [max(0, min(count - 1, event['frame'] + d)) for d in (-3, 0, 3, 9, 18)]
            sheet(selected, samples, f'encoded_{event["id"]}.jpg')
    sheet(sorted(boundaries), boundaries, 'encoded_cut_boundaries.jpg')
    exact_runs = []
    start = None
    for row in rows + [{'frame': count, 'cut': True, 'meanAbsoluteDifference': 1}]:
        if not row['cut'] and row['meanAbsoluteDifference'] == 0:
            if start is None:
                start = row['frame'] - 1
        elif start is not None:
            exact_runs.append({'startFrame': start, 'endFrameExclusive': row['frame'],
                               'durationSeconds': (row['frame'] - start) / spec['fps']})
            start = None
    per_shot = []
    for shot in spec['shots']:
        values = [r['meanAbsoluteDifference'] for r in rows if shot['startFrame'] < r['frame'] < shot['endFrame']]
        per_shot.append({'shot': shot['id'], 'meanFrameDifference': round(float(np.mean(values)), 5),
                         'maximumFrameDifference': max(values)})
    report = {'decodedFrames': count, 'analysisSize': [width, height], 'perShot': per_shot,
              'exactStillRuns': exact_runs,
              'longestExactStillSeconds': max((r['durationSeconds'] for r in exact_runs), default=0),
              'largestWithinShotChanges': sorted((r for r in rows if not r['cut']), key=lambda r: r['meanAbsoluteDifference'], reverse=True)[:12],
              'brightnessJumpsOver20Levels': [r for r in rows if not r['cut'] and abs(r['meanBrightnessChange']) > 20],
              'limits': ['Reduced-resolution frame metrics detect gross freeze/flash issues, not acting quality.',
                         'Contact sheets sample time; they do not establish real-time playback or listening approval.']}
    (out / 'TEMPORAL_QA.json').write_text(json.dumps(report, indent=2), 'utf-8')
    (out / 'frame_differences.json').write_text(json.dumps(rows), 'utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--job', required=True, type=Path)
    parser.add_argument('--video', required=True, type=Path)
    args = parser.parse_args()
    audit(args.job, args.video)
