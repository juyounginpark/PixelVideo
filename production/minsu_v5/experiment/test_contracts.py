import unittest,json
from copy import deepcopy
from pathlib import Path
from state import ExperimentState,validate_object,validate_numeric,signature,numeric_text,timeline_stage

class Contracts(unittest.TestCase):
    def setUp(self):
        self.obj=json.loads((Path(__file__).parent/'fixture.json').read_text('utf-8'))['objects'][0]
        self.receipt={'stateSignature':signature(self.obj),'objectId':'bar','frame':75,'completed':True,'geometryHash':'evaluated-mesh-hash','properties':{'rotationZDegrees':90}}
    def test_complete_then_commit(self):
        s=ExperimentState(self.obj)
        self.assertEqual(s.at(75,self.receipt)['value'],0)
        self.assertEqual(s.at(76,self.receipt)['value'],90)
    def test_missing_completion_fails(self):
        with self.assertRaises(ValueError):ExperimentState(self.obj).at(76)
    def test_actual_geometry_must_agree(self):
        self.receipt['properties']['rotationZDegrees']=45
        with self.assertRaises(ValueError):ExperimentState(self.obj).at(76,self.receipt)
    def test_future_receipt_fails(self):
        self.receipt['frame']=100
        with self.assertRaises(ValueError):ExperimentState(self.obj).at(76,self.receipt)
    def test_previous_version_receipt_fails(self):
        self.obj['geometryVersion']='bar-2'
        with self.assertRaises(ValueError):ExperimentState(self.obj).at(76,self.receipt)
    def test_synthetic_not_real_data(self):
        with self.assertRaises(ValueError):validate_numeric({'kind':'OBSERVATION','meaning':'angle','units':'deg','definition':'rotation Z','source':'SCENE_GEOMETRY'})
    def test_unit_required(self):
        self.obj['displayUnits']=''
        with self.assertRaises(ValueError):validate_object(self.obj)
    def test_definition_required(self):
        self.obj['definition']=''
        with self.assertRaises(ValueError):validate_object(self.obj)
    def test_progress_is_not_evidence(self):
        with self.assertRaises(ValueError):validate_numeric({'kind':'CHAPTER_PROGRESS','meaning':'chapters','source':'REAL_OBSERVATION','value':1,'total':2})
    def test_claim_needs_review(self):
        self.obj['claimStatus']='VERIFIED'
        with self.assertRaises(ValueError):validate_object(self.obj)
    def test_update_before_motion_fails(self):
        self.obj['operation']['updateFrame']=74
        with self.assertRaises(ValueError):validate_object(self.obj)
    def test_illustration_needs_label(self):
        with self.assertRaises(ValueError):validate_numeric({'kind':'STATE','meaning':'illustration','units':'deg','definition':'rotation','source':'ILLUSTRATIVE'})
    def test_nan_numeric_fails(self):
        with self.assertRaises(ValueError):numeric_text({'kind':'STATE','meaning':'angle','units':'deg','definition':'Z rotation','source':'SCENE_GEOMETRY','value':float('nan')})
    def test_stage_order(self):
        self.assertEqual([timeline_stage(self.obj,f) for f in [0,10,20,30,76,77,106]],['INITIAL','CURRENT_VALUE','PREDICT','OPERATE','UPDATE','COMPARE','CONNECT'])

if __name__=='__main__':unittest.main()
