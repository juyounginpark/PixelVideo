"""Authored episode candidate from existing source; no topic selection machinery."""
import json
from pathlib import Path
R=Path(__file__).resolve().parent

def caption(role,start,end,lines,highlight=None,y=None):
    return dict(role=role,startFrame=start,endFrame=end,lines=lines,highlight=highlight or [],y=y)

def make():
    # All times describe the edit, not measured physical time.
    rows=[
      ('hook',0,66,'기','단단한 얼음에서도 발이 밀린다','민수가 첫발을 내딛자 발이 앞으로 밀리고 팔을 펼쳐 균형을 잡는다','단단한데 왜 미끄럽지?','자신감→놀람','발의 이동과 전신 반응을 한 화면에서 연결','HOOK_TITLE','발이 밀리는 프레임에 짧은 줌·미끄럼 SFX','미끄러진 발의 원인을 확인하러 접근'),
      ('inspect',66,144,'기','얼음은 여전히 단단하다','민수가 몸을 낮추고 얼음 표면을 살피며 손을 뻗는다','얼음이 전부 녹은 걸까?','당황→호기심','눈·손·접촉면의 삼각 구도','EXPLANATION_CAPTION','표면을 가리키는 동작과 질문음','민수의 시선에서 신발 접촉부로 컷인'),
      ('contact',144,216,'승','중요한 곳은 물체가 닿는 경계','큰 신발 밑창과 얼음 사이를 확대하며 표면선을 분리한다','닿는 곳에서는 무슨 일이 일어날까?','화면 밖 민수의 신발이 실험 대상','접촉면을 화면 중앙에 크게 제시','MICRO_LABEL','관찰선이 실제 접촉면을 따라 드러난다','접촉면 선을 분자 단면의 최상층으로 연결'),
      ('structure',216,306,'승','내부와 표면 분자의 이동성이 다르다','아래 격자는 자리 주변에서 진동하고 위의 주황 분자는 서로 자리를 바꾼다','같은 얼음인데 겉은 다를까?','관찰 대상이 캐릭터의 의문에 답한다','내부 단면을 넓게 보여 두 층을 동시에 비교','EXPLANATION_CAPTION','표면/내부를 별개 라벨과 명암으로 구분','표면 분자 하나를 따라 경로 확대'),
      ('path',306,372,'승','표면 분자는 위치를 바꾸기 쉽다','추적 중인 물 분자 하나가 이웃 자리로 이동하고 경로가 뒤에 남는다','이 움직임이 미끄러짐과 어떻게 연결될까?','추적 대상에 시선을 집중','3개 분자로 확대하고 실제 이동을 따라 패닝','MICRO_LABEL','주황색 이동 경로를 실제 위치 변화 뒤에 표시','분자 경로와 미끄러지는 접촉체의 방향을 연결'),
      ('discovery',372,456,'전','표면 이동은 낮은 마찰과 연결된다','표면 분자가 재배치되는 동안 접촉체가 옆으로 진행하고 카메라가 따라간다','그래서 저항이 줄어드는구나','발견→이해','접촉체의 움직임을 따라가며 핵심 단어를 위한 위쪽 여백 유지','IMPACT_CAPTION','행동+추적 카메라+저항↓+발견음이 같은 사건','확대 모형에서 실제 크기의 민수로 복귀'),
      ('return',456,516,'전','확대해서 본 현상이 일상 움직임과 연결된다','민수가 몸을 바로 세우고 발을 밀어 균형을 회복한다','얼음이면 언제나 똑같이 미끄러울까?','놀람→생각','전신과 얼음 경로를 함께 보여줌','EXPLANATION_CAPTION','회복 동작에만 짧은 팝','새 질문에 답할 두 조건 비교로 전환'),
      ('compare',516,636,'전','온도가 아주 낮으면 마찰이 큰 사례가 있다','같은 속도로 이동하는 두 강철 접촉체에 다른 크기의 저항 화살표가 생긴다','더 차가우면 더 미끄러울까?','조건을 바꿔 검토','두 조건을 나란히 놓고 같은 방향·속도로 비교','FACT_PANEL','-100°C / -7°C는 실제 논문의 조건, 화살표는 정성 모식도','실험의 조건 한정을 보여준 뒤 다른 요인으로 확장'),
      ('factors',636,744,'결','온도 외에 압력·속도·접촉 조건도 중요하다','접촉체가 눌리고 지나가는 경계가 강조되며 세 조건이 순서대로 밝혀진다','한 가지 원인만으로 설명할 수 있나?','성급한 단정 대신 확인','접촉부 측면으로 전환해 누르는 방향과 진행 방향 분리','EXPLANATION_CAPTION','온도/압력/속도를 동작의 순서에 맞춰 표시','모형의 한계를 짚고 처음 행동의 전후를 비교'),
      ('before_after',744,846,'결','민수의 이동 결과가 달라졌다','얼음 위 출발 위치의 윤곽과 이동한 민수, 그 사이 경로를 한 화면에서 비교한다','처음 어디서 출발했지?','이해→작은 성공','위에서 내려다보는 구도로 출발·도착을 함께 제시','MICRO_LABEL','실제 애니메이션의 전후 위치만 표시, 거리 숫자 없음','결과에서 인물 얼굴과 전체 공간으로 돌아감'),
      ('result',846,966,'결','단단한 속과 움직이기 쉬운 표면을 구분한다','민수가 손으로 얼음을 가리킨 뒤 고개를 끄덕이고 다시 균형 잡힌 자세로 이동한다','속이 단단한 것과 표면이 미끄러운 것은 다르구나','이해→자신감','따뜻한 인물과 차가운 얼음이 분리되는 마무리 전신','RESULT_TITLE','단단한 속 / 움직이는 표면을 다른 색·크기로 결론화','다시 발을 내딛는 동작으로 도입 질문에 돌아감'),
      ('loop',966,1050,'결','새로 이해한 상태에서 첫 행동으로 돌아간다','민수가 한 발을 들고 같은 방향으로 나아가며 도입의 발동작으로 연결된다','다시 보면 발밑의 무엇을 보게 될까?','자신감→다음 동작 집중','도입과 같은 카메라 축으로 복귀','EXPLANATION_CAPTION','불필요한 추가 효과 없이 발동작 연결','첫 컷의 발 이동으로 하드컷 연결')
    ]
    caps={
      'hook':[caption('HOOK_TITLE',4,64,['단단한 얼음,','왜 미끄러울까?'],['왜 미끄러울까?'],250)],
      'inspect':[caption('EXPLANATION_CAPTION',73,139,['분명 단단한데…'],[],1360)],
      'contact':[caption('EXPLANATION_CAPTION',153,212,['얼음 전체 말고,','닿는 표면을 보자'],['표면'],1350)],
      'structure':[caption('EXPLANATION_CAPTION',224,303,['속과 겉은','움직임이 다르다'],['움직임'],1350)],
      'path':[caption('EXPLANATION_CAPTION',314,369,['표면 분자는','자리를 옮기기 쉽다'],['표면 분자'],1360)],
      'discovery':[caption('MICRO_LABEL',375,453,['표면 이동으로 설명한 연구'],[],285),caption('IMPACT_CAPTION',400,447,['저항 ↓'],['저항'],405)],
      'return':[caption('EXPLANATION_CAPTION',462,513,['그럼 더 차가우면?'],['더 차가우면'],300)],
      'compare':[caption('HOOK_TITLE',524,577,['더 차가운 쪽이…'],[],270),caption('FACT_PANEL',578,634,['강철 구슬-얼음 실험','비교한 두 온도'],['두 온도'],345),caption('EXPLANATION_CAPTION',580,632,['오히려 마찰이 컸다'],['마찰'],1400)],
      'factors':[caption('EXPLANATION_CAPTION',641,698,['온도·압력·속도도','함께 영향을 준다'],['온도','압력','속도'],1350),caption('EXPLANATION_CAPTION',700,741,['한 가지로 다 설명되진 않아'],[],1360)],
      'before_after':[caption('EXPLANATION_CAPTION',752,841,['얼음이 전부 녹아야','미끄러운 건 아니다'],['전부'],1370)],
      'result':[caption('RESULT_TITLE',853,960,['단단한 속','움직이는 표면'],['표면'],255)],
      'loop':[caption('EXPLANATION_CAPTION',972,1042,['비밀은, 발이 닿는 곳'],['닿는 곳'],285)]
    }
    events={'hook':(24,'SURPRISE','minsu',2,'slip'),'inspect':(99,'QUESTION','minsu',1,'inspect'),
            'contact':(178,'EXPERIMENT','surface',1,'contact'),'structure':(252,'COMPARISON','surface',1,'structure'),
            'path':(326,'EXPERIMENT','molecule',1,'path'),'discovery':(400,'DISCOVERY','slider',3,'discovery'),
            'return':(487,'REALIZATION','minsu',1,'recover'),'compare':(578,'COMPARISON','surface',2,'compare'),
            'factors':(674,'EXPERIMENT','slider',1,'pressure'),'before_after':(799,'COMPARISON','minsu',1,'compare_positions'),
            'result':(874,'REALIZATION','minsu',1,'understand')}
    shots=[]
    modes={'hook':'whole','inspect':'whole','contact':'contact','structure':'internal','path':'path','discovery':'contact','return':'whole','compare':'conditions','factors':'internal','before_after':'before_after','result':'whole','loop':'whole'}
    for i,row in enumerate(rows):
        phase,start,end,beat,info,visual,question,reaction,camera,role,emphasis,transition=row
        action={'id':phase,'startFrame':start,'endFrame':end,'target':events[phase][2] if phase in events else 'minsu','visibleChange':visual}
        ev=[]
        if phase in events:
            f,kind,target,intensity,sound=events[phase]
            e={'id':f'event_{i}','frame':f,'type':kind,'target':target,'intensity':intensity,'actionId':phase}
            if phase=='discovery':e['text']='저항 ↓'
            if phase=='compare':e['data']={'label':'강철-얼음 실험','value':'온도 비교','provenance':'Weber et al. 2018 Fig.1, DOI 10.1021/acs.jpclett.8b01188'}
            ev=[e]
        shots.append(dict(id=f'SHOT_{i+1:02}',phase=phase,startFrame=start,endFrame=end,StoryBeat=beat,NewInformation=info,
                          PrimaryVisualEvent=visual,ViewerQuestion=question,CharacterReaction=reaction,CameraPurpose=camera,
                          CaptionRole=role,EmphasisEvent=emphasis,TransitionReason=transition,visualMode=modes[phase],
                          actions=[action],events=ev,captions=[],typography=caps[phase],diagram=phase in ('structure','path','discovery','compare','factors')))
    return dict(id='MINSU_EP06_V31_ICE',title='단단한 얼음, 왜 미끄러울까?',topic='얼음이 미끄러운 이유',fps=30,durationFrames=1050,
                nativeSize=[540,960],outputSize=[1080,1920],shots=shots,audioMood='observation',audioTrack='curious_desert_100',
                source={'local':'research/namuwiki/listing.txt','draftRow':3,'status':'candidate_pending_sample_gate'},
                scientificScope='2018/2021 연구에서 제시한 표면 이동과 마찰의 연결. 모든 조건의 단일 확정 원인으로 표현하지 않음.',
                scientificSources=['https://doi.org/10.1021/acs.jpclett.8b01188','https://doi.org/10.1103/PhysRevX.11.011025'],
                sampleFrames=[306,456])

if __name__=='__main__':
    spec=make();(R/'ep06').mkdir(exist_ok=True)
    (R/'ep06/episode.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),'utf-8')
    lines=['# EP06 사건 콘티 — 제작 초안','', '기존 공급 목록 3번 검토. 5초 샘플 통과 후 제작 확정. 초 단위는 편집 시간이며 물리 시간 아님.','']
    for shot in spec['shots']:
        lines+=['## '+shot['id']+' / '+str(shot['startFrame']/30)+'–'+str(shot['endFrame']/30)+'초','']
        lines += [f'- **{k}**: {shot[k]}' for k in ('StoryBeat','NewInformation','PrimaryVisualEvent','ViewerQuestion','CharacterReaction','CameraPurpose','CaptionRole','EmphasisEvent','TransitionReason','visualMode')]
        lines+=['']
    (R/'STORYBOARD.md').write_text('\n'.join(lines),'utf-8')
    print('EPISODE_DRAFT_WRITTEN')
