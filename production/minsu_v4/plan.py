"""One structured episode draft; explicit existing-source candidate, not a selector."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
def dump(p,data):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf-8')
def caption(role,ko,en,start,end,y=1340,highlight=()):
    return dict(role=role,lines=ko.split('|'),english=en.split('|'),start=start,end=end,y=y,highlight=list(highlight))
def make():
    rows=[
    ('hook',90,'기','관측판의 두 별','왜 예상보다 빠르지?','같은 바깥 궤도에서 관측 별이 예상 별보다 앞선다','민수가 관측판을 켜자 노란 별이 점선 예상 위치를 앞지르고 민수가 손을 멈춘다','빛나는 물질의 질량만으로 예상한 회전과 실제 관측의 불일치','자신감→멈칫→호기심','TABLE',[0,-.25,.75],4.6,'예상보다|너무 빠른 별','Why are these stars|faster than expected?','HOOK_TITLE',220,'OBSERVE',26,'outer', ['빠른']),
    ('observe',90,'승','민수와 망원경','무엇을 비교한 걸까?','별빛은 질량 추정의 단서다','망원경에 몸을 기울이고 관측판의 밝은 별 부분을 손으로 가리킨다','관측 장면은 역할극이며 실측 영상이 아님','호기심→집중','PORTRAIT',[0,0,.82],3.8,'별빛으로 질량을|추정해 봤어요','Starlight helps us estimate|how much matter is there.','BODY_CAPTION',1320,'ACT',38,'head',['질량']),
    ('expected',105,'승','질량 모형과 바깥 별','그 질량이면 어떻게 돌까?','중심에 집중된 빛나는 물질만을 반영한 바깥쪽 예상은 느리다','밝은 중심은 남기고 바깥 궤도 별과 짧은 이동 흔적을 보여준다','예상 회전은 질량 분포로 계산; 모든 은하 전체에 케플러 법칙을 일괄 적용하지 않는다','민수는 화면 밖에서 비교를 수행','MACRO',[0,0,0],4.1,'보이는 질량만 넣으면|바깥쪽은 느릴 텐데','With visible matter alone,|outer stars should move more slowly.','BODY_CAPTION',1320,'COMPARE',38,'outer',['보이는 질량']),
    ('actual',105,'승','같은 반지름의 실제/예상 별','관측은 얼마나 다른가?','실제 바깥쪽 회전 속력은 예상보다 크다','동일 궤도 위 노란 관측 별이 흰 점선 예상 별을 앞서 나간다','대표적인 회전곡선의 정성 비교; 시간·거리·속력은 실측값 아님','민수 관측 반응은 다음 컷으로 연결','MACRO',[0,0,0],4.1,'실제 별은|더 빠르게 돌아요','But the observed stars|move faster than predicted.','IMPACT_CAPTION',230,'COMPARE',40,'outer',['빠르게']),
    ('gravity',105,'전','별의 운동 방향과 안쪽 중력','빠른 별은 무엇이 필요한가?','원운동에는 안쪽으로 향하는 중력이 필요하다','별이 직선으로 갈 방향과 중심으로 당기는 화살표가 순서대로 생겨 곡선 궤도를 만든다','구심 가속도 v²/r의 방향 설명, 뉴턴 역학 원궤도 단순화','인물 대신 움직이는 별을 단일 주인공으로','MACRO',[0,0,0],4.3,'별을 휘어 돌리는 힘,|중력이에요','Gravity bends the star’s path|toward the center.','BODY_CAPTION',1320,'ACT',30,'outer',['중력']),
    ('shortage',105,'전','동일 반지름의 느린/빠른 궤도','같은 궤도에서 더 빠르다면?','같은 반지름에서 빠른 원운동에는 더 큰 안쪽 가속도가 필요하다','위쪽 느린 별과 아래쪽 빠른 별에 각기 짧고 긴 안쪽 화살표를 연결한다','필요 중력은 속력의 제곱/반지름; 화면은 정성 모식도','비교에 집중','MACRO',[0,0,0],5.9,'같은 궤도라면, 빠를수록|더 큰 중력이 필요해요','At the same orbit size, faster stars|need a stronger inward pull.','BODY_CAPTION',1340,'COMPARE',32,'outer',['더 큰 중력']),
    ('halo',120,'전','빛나는 은하 주변의 추론 헤일로','필요한 중력은 어디에서 오나?','보이지 않는 추가 질량을 포함하면 관측을 설명할 수 있다','작은 발광 은하 주위로 넓은 민트색 점선 구가 드러난다','헤일로는 추론 모형, 직접 촬영한 물질이나 빛나는 가스가 아니다','발견의 중심; 인물 생략','TABLE',[0,0,0],5.1,'보이지 않는 질량을|더하면 설명돼요','Adding unseen mass|can explain the motion.','IMPACT_CAPTION',230,'DISCOVER',44,'galaxy',['질량']),
    ('fit',90,'결','민수와 수정한 관측판','처음의 불일치가 해결됐나?','추가 질량을 포함한 모형이 빠른 관측 별을 따라간다','민수가 모형 스위치를 누르자 점선 예상 별이 노란 관측 별과 겹친다','주류 암흑물질 모형의 설명, 가정 없이 입자 정체를 확정한 실험 아님','신중함→납득→작은 끄덕임','TABLE',[0,-.25,.75],4.6,'움직임에서 찾은|암흑물질의 단서','The motion is evidence|for dark matter.','BODY_CAPTION',1320,'RESOLVE',42,'outer',['암흑물질']),
    ('identity',90,'결','헤일로 표시가 사라진 은하','암흑물질은 검은 구름인가?','그림의 색은 표시일 뿐이며 물질 정체는 미확인이다','민수가 표시를 끄자 점선 구는 사라져도 별은 계속 돈다','빛으로 직접 보지 못함; 추론 표시와 관측 대상을 구분','이해→확인','TABLE',[0,0,0],4.6,'색은 설명용 표시예요|정체는 아직 몰라요','The color is only a guide.|Its identity is still unknown.','BODY_CAPTION',1320,'ACT',38,'galaxy',['정체']),
    ('conclusion',120,'결','민수와 처음의 빠른 별','왜 예상보다 빨랐나?','처음 계산에서 보이지 않는 질량을 빠뜨렸을 수 있다','처음의 두 궤적을 겹쳐 확인하고 민수가 관측판을 닫지 않고 만족스럽게 바라본다','중력 효과로 추가 질량을 추론한다는 결론','납득→미소','TABLE',[0,-.25,.75],4.6,'빛으로 안 보여도|중력은 남아요','Unseen matter leaves|a gravitational signature.','RESULT_TITLE',220,'RESOLVE',42,'outer',['중력'])]
    shots=[];cursor=0
    for i,row in enumerate(rows):
        phase,n,beat,subject,question,info,action,meaning,emotion,cam,aim,scale,ko,en,role,y,preset,event,target,hi=row
        end=cursor+n;cap=caption(role,ko,en,4,n-4,y,hi)
        shots.append(dict(id=f'S{i+1:02}',phase=phase,startFrame=cursor,endFrame=end,narrativeRole=beat,primarySubject=subject,viewerQuestion=question,newInformation=info,visualAction=action,scientificMeaning=meaning,characterEmotion=emotion,cameraPlan=dict(preset=cam,aim=aim,scale=scale,push=.025),captionPlan=[cap],emphasisEvent=dict(frame=event,type={'DISCOVER':'DISCOVERY','COMPARE':'COMPARISON','ACT':'EXPERIMENT','RESOLVE':'REALIZATION','OBSERVE':'SURPRISE'}[preset],preset=preset,target=target,action=phase),nextShotConnection='처음 현상을 원리로 해석하며 닫음' if i==len(rows)-1 else rows[i+1][3]+'로 관심 대상을 연결',scene=dict(adapter='dark_matter',mode=phase,action=phase,seed=407,assetIds=['observatory_set','galaxy_model','orbital_comparison','gravity_macro','inferred_halo'],materialIds=['V4_palette'],speed=.75),labels=[]))
        cursor=end
    spec=dict(id='MINSU_EP07_V4_DARK_MATTER',topicId='namuwiki-draft-08',topic='암흑물질',status='candidate_sample_only',configVersion='4.0.0',fps=30,durationFrames=cursor,goal='회전 관측→필요 중력→추가 질량의 추론을 무음에서도 이해',newAssets=['observatory_set','galaxy_model','orbital_comparison','gravity_macro','inferred_halo'],sampleShots=['S05','S06'],shots=shots,
      storyMap=dict(phenomenon='은하 바깥 별이 보이는 질량만으로 예상한 것보다 빠름',situation='민수가 관측실에서 예상 궤적과 관측 궤적을 겹침',expectation='보이는 질량만으로 속력을 설명할 수 있을 것',contradiction='실제 별이 예상보다 앞섬',clue='같은 반지름의 빠른 공전',mechanism='큰 v²/r에 필요한 중력을 보이는 질량만으로 충족 못 함; 추가 질량으로 설명',payoff='민트 헤일로 모형을 켜자 예상과 관측 궤적이 겹침',takeaway='빛으로 안 보이는 질량도 중력 효과로 추론할 수 있음; 정체는 미확인'),
      science=dict(phenomenon='은하 회전곡선',cause='질량 분포가 만드는 중력',movingObject='대표 별/가스 추적자의 대리 별',observableResult='바깥 회전 속력의 예상-관측 차이',conditions='정성적 대표 나선은하, 원궤도와 뉴턴 중력 가정. 모든 은하가 똑같은 곡선인 것은 아님',simplification='모형: 색·시간·크기 확대, 실측 좌표/수치가 아님; 헤일로는 추론 표시'),
      evidence=[dict(url='https://science.nasa.gov/mission/hubble/science/science-behind-the-discoveries/hubble-dark-matter/',claim='바깥 별 회전과 보이지 않는 질량, 헤일로',location='Rubin paragraph / invisible matter / haloes'),dict(url='https://science.nasa.gov/dark-matter/',claim='정체 미확인; dark는 검은 색이라는 뜻이 아님',location='Dark Matter Versus Dark Energy; candidates')],
      source=dict(path='research/namuwiki/TOPIC_LIST_DRAFT.md',row=8,name='암흑물질',sha256=hashlib.sha256((ROOT/'research/namuwiki/TOPIC_LIST_DRAFT.md').read_bytes()).hexdigest(),criteria='prompts/MYSTERY_100_v1.md'),audio=dict(track='curious_desert_100',mood='mechanism',tts=False))
    # Labels are bilingual semantic data, not topic-specific overlays hidden in code.
    labelsets={
    'hook':[('MICRO_LABEL','예상 / 관측','Predicted / observed',530)],
    'expected':[('STATUS_HUD','보이는 질량만','Visible mass only',250)],
    'actual':[('MICRO_LABEL','점선: 예상  노랑: 관측','Dashed: predicted  Yellow: observed',1220)],
    'gravity':[('STATUS_HUD','원리 모식도','Schematic, not measured scale',185)],
    'shortage':[('MICRO_LABEL','느린 별 / 같은 반지름','Slower / same orbit size',420),('MICRO_LABEL','빠른 별 / 같은 반지름','Faster / same orbit size',950)],
    'halo':[('FACT_PANEL','추가 질량 모형','Inferred mass model',1190)],
    'fit':[('MICRO_LABEL','모형과 관측의 일치','Model matches observation',530)],
    'identity':[('STATUS_HUD','헤일로 = 질량 분포 모형','Halo = a mass distribution model',235)],
    'conclusion':[('MICRO_LABEL','NASA / 은하 회전 근거','NASA / galaxy rotation evidence',1520)]}
    for s in shots:
        s['labels']=[caption(role,ko,en,0,s['endFrame']-s['startFrame'],y) for role,ko,en,y in labelsets.get(s['phase'],[])]
    return spec
if __name__=='__main__':
    p=R/'ep07/episode.json'
    if p.exists():raise SystemExit('Draft already exists; edit explicitly, never reset reviewed episode')
    dump(p,make());print('Episode candidate',make()['durationFrames'],'frames')
