"""Write delivery facts after the actual-image review and measured cache rerun."""
from datetime import datetime,timezone,timedelta
from common import R,ROOT,read,write,sha

def main():
    job=R/'ep07';final=job/'final';review=final/'review'
    technical=read(final/'TECHNICAL_QA.json');cache=read(final/'CACHE_PROOF.json')
    assert technical['status']=='PASS' and cache['status']=='PASS'
    comp=read(final/'compose.json');video=ROOT/'exports/MINSU_EP07_V4_DARK_MATTER.mp4'
    assert sha(video)==cache['afterSha256']==read(review/'decode_qa.json')['sha256']
    stamp=datetime.now(timezone(timedelta(hours=9),'Asia/Seoul')).isoformat(timespec='seconds')
    evidence=['overview.jpg','REFERENCE_COMPARISON.jpg','S01_sequence.jpg','S05_sequence.jpg',
              'S06_sequence.jpg','S07_sequence.jpg','S08_sequence.jpg','S10_060.png','S02_045.png',
              'S02_sequence.jpg','S03_052.png']
    assert all((review/p).exists() for p in evidence)
    editorial=dict(decision='DELIVER_WITH_EDITORIAL_LIMITS',reviewedAt=stamp,
        reviewer='Codex: actual decoded MP4 images and sequences',videoSha256=sha(video),
        evidence=evidence,technicalPassUsedAsArtApproval=False,
        findings=[
            '0–3초: 같은 궤도에서 흰 예상 표시보다 노란 관측 별이 앞서는 사건을 보여준다. 제목 없이도 이동 차이는 보이며 예상/관측의 뜻은 범례로 전달한다.',
            '3–6초: 민수가 관측판에 몸을 기울인다. 최종 QA에서 바깥 별 잘림을 발견해 S02 카메라만 다시 렌더링했고 수정 후 판과 별이 보인다.',
            '6–13초: 예상 모형은 흰 외곽선, 관측은 노랑으로 기호를 통일했다. 두 컷의 비교가 새 정보를 만든다.',
            '13–20초: 진행 방향과 안쪽 중력, 같은 반지름에서 속력에 따른 필요 중력을 순차적으로 보여준다. 후반 화살표와 자막 겹침을 실제 샘플 검수에서 수정했다.',
            '20–24초: 추론 헤일로 전개, 추가 질량 타이포, 카메라 확대가 핵심 발견에 집중된다. 정보창은 실제 촬영한 물질이 아닌 모형임을 알린다.',
            '24–28초: 손의 조작과 모형 변화가 연결되고 궤적이 겹친 뒤에만 일치 라벨이 나온다.',
            '28–35초: 모형의 색과 미확인 정체를 구분한 뒤, 처음의 속력 불일치를 중력의 흔적으로 정리한다.',
            '한글과 영어가 분리된 계층으로 나타나며 선택 단어만 강조한다. 실제 출력에서 별/얼굴과 자막 충돌을 확인했다.',
            '540×960 실제 3D의 계단형 경계와 제한 팔레트, 독립 UI를 확인했다. 캐릭터·무대의 재질은 일관되며 임의 사진/서체가 섞이지 않는다.',
            '실제 ref3/ref4와 EP06/EP07 대표 프레임을 나란히 비교했다. 상황→개념→적용의 연결과 자막 계층은 개선되었다.'
        ],limits=[
            '레퍼런스 4 수준의 섬세한 전신 연기와 감정 연출까지 동등하다고 판정하지 않는다. 현재 손짓·기울임·고개 반응은 단순하다.',
            '영어 보조 자막은 36px이며 한글보다 읽기 부담이 크다. 실제 휴대폰/영어 모어 화자/대중 시청자 테스트는 하지 않았다.',
            '궤도·중력·헤일로는 정성적 모식도다. 중심 기호는 질량 분포를 단순화하며 실제 단일 별이나 관측 좌표를 뜻하지 않는다. N-body 시뮬레이션이 아니다.',
            '무음에서도 인과를 따라갈 수 있도록 구성했지만 범례와 짧은 설명이 필요하다. 시청 유지율과 설명 이해도는 미측정이다.',
            '실제 MP4의 전 프레임 디코드와 0.267초 간격 연속 프레임을 검수했다. 사람의 실시간 재생·청취 검수는 하지 않았다.'
        ])
    write(final/'EDITORIAL_QA.json',editorial)
    first=read(final/'first_last_render.json');firstcomp=read(final/'first_compose.json')
    revision=read(final/'s02_revision_last_render.json');revisioncomp=read(final/'s02_revision_compose.json')
    assets=read(R/'config/ASSET_MANIFEST.json')
    baseline=read(R/'review/preservation_before.json')
    changed=[p for p,h in baseline.items() if sha(ROOT/p)!=h];assert not changed
    delivery=dict(completedAt=stamp,episode='EP07',topicId='namuwiki-draft-08',topic='암흑물질',
        output=str(video),sha256=sha(video),bytes=video.stat().st_size,
        durationSeconds=comp['duration'],frames=comp['frameCount'],format='1080×1920 / 30fps / H.264 + AAC',
        subtitles=['Korean primary','English secondary'],tts=False,
        coreModules=['NarrativeDirector','TypographyTheme','CharacterDirector','event-driven camera/SFX presets','render.py native cache','compose.py UI/audio cache','two-stage QA'],
        timingsSeconds=dict(initialFullNative=first['totalSeconds'],initialFullCompose=firstcomp['totalSeconds'],
            finalS02RevisionNative=revision['totalSeconds'],finalS02RevisionCompose=revisioncomp['totalSeconds'],
            warmCommand=cache['warmCommandWallSeconds']),
        timingsScope='Initial full render plus one final S02 correction. Excludes earlier design trials, sample, preview, QA and planning; see run history for those.',
        finalCorrection=dict(renderedFrames=revision['renderedFrames'],reusedFrames=revision['reusedFrames'],uiCacheHits=revisioncomp['uiCacheHits']),
        assets=dict(reusedCount=len(assets['reused']),reused=assets['reused'],newGroupCount=len(assets['new']),newGroups=assets['new'],countUnit='named reusable asset types / authored groups, not mesh count'),
        optimization=dict(cacheProof='final/CACHE_PROOF.json',sourceFilesPreserved=len(baseline),sourceChanges=changed,
            externalLLMAPICalls=0,additionalEditorialRevisionBatches=8,promptRange='P-034…P-041',
            externalTokenSavingsMeasured=False,currentCodexTokenUsage='not available',maxHeavyRenderWorkers=1),
        technicalQA=dict(status=technical['status'],checkedFrames=technical['checkedNativeAndUIFrames'],fontFallbacks=technical['fontCoverage']['fallbacks'],
            audioOffsetSeconds=technical['aacDecodedAlignmentSeconds'],audioCorrelation=technical['aacCorrelation'],testsPassed=11),
        editorialQA='final/EDITORIAL_QA.json',editorialDecision=editorial['decision'],
        referenceComparison='final/review/REFERENCE_COMPARISON.jpg',
        automationLimit='Structured episode input and supported topic adapter required. No automatic arbitrary-topic asset generation or automatic aesthetic approval.')
    write(job/'DELIVERY.json',delivery)
    write(job/'state.json',dict(stage='delivered',output=str(video),editorialAutomaticPass=False,editorialReview='final/EDITORIAL_QA.json',technicalQA='PASS'))
    log=ROOT/'PROMPT_LOG.md';marker='### U-088/089 — EP07 V4 납품 기록'
    if marker not in log.read_text('utf-8'):
        with log.open('a',encoding='utf-8') as f:
            f.write(f'\n\n{marker}\n{stamp}. P-033~P-041 실행. 결과: exports/MINSU_EP07_V4_DARK_MATTER.mp4 (35초, 한글+영어 보조, 로컬 BGM/SFX, TTS 없음). 실제 기록: production/minsu_v4/ep07/DELIVERY.json. 기술 QA PASS와 편집 한계는 분리 기록. 공급 원본 {len(baseline)}개 파일 보존, 추가 외부 LLM API 호출 0.\n')
    print('DELIVERED',video)

if __name__=='__main__':main()
