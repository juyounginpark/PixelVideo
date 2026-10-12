"""Typed experiment state. Animation completion is necessary, not scientific proof."""
from copy import deepcopy
import hashlib
import json
import math

OPERATIONS = {'Rotate','Squash','Stretch','Bend','Flatten','Cut','Pierce','Join','Open','Close','Morph','Compare','ValueUpdate'}
KINDS = {'CHAPTER_PROGRESS','STATE','COMPARISON','OUTCOME','OBSERVATION'}
SOURCES = {'SCENE_GEOMETRY','REAL_OBSERVATION','ILLUSTRATIVE'}
REQUIRED = {'objectId','objectType','geometryVersion','operation','observedProperties','previousValue','currentValue','displayUnits','claimStatus','evidenceStatus'}

def signature(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def validate_object(obj):
    if REQUIRED - obj.keys(): raise ValueError('Missing object state: '+str(REQUIRED-obj.keys()))
    if not obj['objectId'] or not obj['geometryVersion']: raise ValueError('Unversioned geometry')
    op = obj['operation']
    if op['type'] not in OPERATIONS: raise ValueError('Unsupported operation')
    if not 0 <= op['startFrame'] < op['completeFrame'] <= op['updateFrame']: raise ValueError('Operation/update order')
    if not obj['displayUnits'] or not obj.get('definition'): raise ValueError('Units and definition required')
    if obj['evidenceStatus'] not in SOURCES: raise ValueError('Unknown evidence status')
    if obj['claimStatus'] not in {'MODEL_STATE','VERIFIED','UNRESOLVED','DISPUTED','ILLUSTRATIVE'}: raise ValueError('Unknown claim status')
    if obj['evidenceStatus']=='REAL_OBSERVATION' and not obj.get('sourceRefs'): raise ValueError('Real observations require sources')
    if obj['claimStatus']=='VERIFIED' and (not obj.get('sourceRefs') or not obj.get('scientificReview')): raise ValueError('Verified claim requires independent review')
    if obj['evidenceStatus']=='ILLUSTRATIVE' and obj['claimStatus']!='ILLUSTRATIVE': raise ValueError('Illustration cannot be evidence')
    prop = obj['observedProperties']
    if len(prop)!=1 or not isinstance(prop[0],str): raise ValueError('One explicit property per state channel')
    for key in ['previousValue','currentValue']:
        if not isinstance(obj[key],(int,float)) or isinstance(obj[key],bool) or not math.isfinite(obj[key]): raise ValueError('Finite numeric state required')
    return obj

def validate_numeric(item):
    if item['kind'] not in KINDS: raise ValueError('Unknown numeric UI kind')
    if not item.get('meaning'): raise ValueError('Numeric meaning missing')
    if item['kind']=='CHAPTER_PROGRESS':
        if item.get('source')!='EDITORIAL_PROGRESS': raise ValueError('Chapter index is editorial metadata')
        if not 1 <= item['value'] <= item['total']: raise ValueError('Chapter range')
    elif item['kind']=='OUTCOME':
        if not item.get('criterion') or item['value'] not in {'SUCCESS','FAILURE','PENDING'}: raise ValueError('Outcome criterion required')
    else:
        if not item.get('units') or not item.get('definition'): raise ValueError('Undefined number')
        if item.get('source') not in SOURCES: raise ValueError('Numeric provenance required')
        if item['kind']=='OBSERVATION' and (item['source']!='REAL_OBSERVATION' or not item.get('sourceRefs')): raise ValueError('No synthetic observed data')
        if item['source']=='REAL_OBSERVATION' and not item.get('sourceRefs'): raise ValueError('Missing observation source')
        if item['source']=='ILLUSTRATIVE' and not item.get('visibleDisclaimer'): raise ValueError('Illustration must be labeled')
    return item

def numeric_text(item):
    """Five explicitly typed HUD channels share formatting, never provenance."""
    validate_numeric(item)
    kind=item['kind']
    if kind=='CHAPTER_PROGRESS':return f"비교 {item['value']} / {item['total']}"
    if kind=='OUTCOME':return {'SUCCESS':'성공','FAILURE':'실패','PENDING':'확인 중'}[item['value']]
    def value(v):
        if not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v):raise ValueError('Invalid numeric value')
        return f'{v:g}{item["units"]}'
    if kind=='COMPARISON':return f"예상 {value(item['expected'])} / 결과 {value(item['actual'])}"
    return value(item['value'])

def timeline_stage(obj,frame):
    op=obj['operation'];start=op['startFrame'];complete=op['completeFrame'];update=op['updateFrame']
    if frame<0:raise ValueError('Negative frame')
    if frame<start/3:return 'INITIAL'
    if frame<start*2/3:return 'CURRENT_VALUE'
    if frame<start:return 'PREDICT'
    if frame<=complete:return 'OPERATE'
    if frame<=update:return 'UPDATE'
    if frame<update+30:return 'COMPARE'
    return 'CONNECT'

class ExperimentState:
    def __init__(self, obj): self.obj = deepcopy(validate_object(obj))

    def at(self, frame, receipt=None):
        obj = self.obj; op = obj['operation']; committed = frame >= op['updateFrame']
        if committed:
            if receipt is None: raise ValueError('No geometry completion receipt')
            if receipt['stateSignature']!=signature(obj) or receipt['objectId']!=obj['objectId']: raise ValueError('Stale/foreign receipt')
            if not op['completeFrame'] <= receipt['frame'] <= frame: raise ValueError('Future or premature completion')
            if not receipt.get('geometryHash') or not receipt.get('completed'): raise ValueError('Geometry not complete')
            actual = receipt['properties'][obj['observedProperties'][0]]
            if not math.isclose(actual,obj['currentValue'],abs_tol=1e-5): raise ValueError('Geometry and value disagree')
        return {'value': obj['currentValue'] if committed else obj['previousValue'], 'units':obj['displayUnits'],
                'pending': op['startFrame'] <= frame < op['updateFrame'], 'committed':committed,
                'semantic':'CONFIRMED' if committed else 'IMPORTANT_NUMBER', 'evidenceStatus':obj['evidenceStatus']}

def validate_story(story):
    required = ['QUESTION','COMPETING_HYPOTHESES','OBSERVE','EXPERIMENT','DISCOVERY','TRANSFER','CONCLUSION','PARTICIPATE']
    if [s['role'] for s in story]!=required: raise ValueError('Experiment story progression missing')
    if any(not s.get('newInformation') or not s.get('visualAction') for s in story): raise ValueError('Empty narrative stage')
    if story[-2].get('resolvesQuestion')!=story[0].get('questionId'): raise ValueError('Conclusion must answer initial question')
    if story[5].get('conceptId')!=story[4].get('conceptId') or not story[5].get('differentObject'): raise ValueError('Transfer must apply same concept to another object')
    if story[-1].get('newTopic'): raise ValueError('Participation must stay within the concept')
    return {'structure':'PASS','editorialApproval':False}
