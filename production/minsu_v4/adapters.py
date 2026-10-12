"""Explicit supported scene adapters; no missing-source or unknown-topic fallback."""
SUPPORTED={'dark_matter':{'topicId':'namuwiki-draft-08','phases':{'hook','observe','expected','actual','gravity','shortage','halo','fit','identity','conclusion'}}}
def validate_adapter(spec):
    for shot in spec['shots']:
        adapter=shot['scene']['adapter']
        if adapter not in SUPPORTED:raise ValueError('A new topic needs its own reviewed scene adapter: '+adapter)
        entry=SUPPORTED[adapter]
        if spec['topicId']!=entry['topicId']:raise ValueError('Topic/scene adapter mismatch; no fallback allowed')
        if shot['phase'] not in entry['phases']:raise ValueError('Unknown action/scene mode; no default scene allowed')
