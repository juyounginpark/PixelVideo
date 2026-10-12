"""Reuse licensed local music/SFX and shape the music at narrative events."""
from audio import AudioSynchronizer,read_wav,write_wav,normalize,measure,SR
from common import read,write
import numpy as np

def build(duration,events,folder,settings,timeline_offset=0):
 mix=AudioSynchronizer().build(duration,events,folder,track_id=settings['track'],mood=settings['mood'])
 bgm=read_wav(folder/'bgm.wav');sfx=read_wav(folder/'sfx.wav');keys=settings['energy']
 times=np.arange(len(bgm))/SR+timeline_offset
 db=np.interp(times,[p['time'] for p in keys],[p['db'] for p in keys]);bgm*=10**(db[:,None]/20)
 write_wav(folder/'bgm.wav',bgm);write_wav(folder/'mix_raw.wav',bgm+sfx)
 measurement=normalize(folder/'mix_raw.wav',mix,-19)
 qa=read(folder/'audio_qa.json');qa.update(energyKeyframes=keys,timelineOffset=timeline_offset,bgmMeasurement=measure(folder/'bgm.wav'),mixMeasurement=measurement,peakPassed=float(measurement['input_tp'])<=-1,arrangementReview='Event alignment and amplitude envelope reviewed; no human listening approval.')
 windows=[float(np.sqrt(np.mean(bgm[i:i+SR//2]**2))) for i in range(SR//2,max(SR//2+1,len(bgm)-SR),SR//2)]
 qa.update(minimumHalfSecondBgmRMS=min(windows),bgmCoveragePassed=all(v>.0001 for v in windows),intentionalPreDiscoveryDip='15.25-15.55s, -20 dB authored music gain')
 write(folder/'audio_qa.json',qa);return mix
