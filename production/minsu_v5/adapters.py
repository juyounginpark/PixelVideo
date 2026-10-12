def validate_adapter(spec):
 if spec['topicId']!='namu-cache-listing-023':raise ValueError('No reviewed visual adapter for this source item')
 if any(s['scene']['adapter']!='red_rain' for s in spec['shots']):raise ValueError('Unsupported adapter; no fallback topic')
