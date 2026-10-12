import sys
from common import R,ROOT
from run import call,BLENDER
call('color_render',[BLENDER,'-b','--python',R/'render.py','--','--quality','preview','--shots','S03'])
call('color_compose',[sys.executable,R/'compose.py','--quality','preview','--shots','S03','--output',ROOT/'exports/MINSU_V4_EXPECTED_COLOR_REVIEW.mp4'])
call('color_audit',[sys.executable,R/'audit_video.py','--video',ROOT/'exports/MINSU_V4_EXPECTED_COLOR_REVIEW.mp4','--out',R/'ep07/preview/color_review','--shots','S03'])
