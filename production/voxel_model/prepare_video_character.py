"""Generate a video character through the same local OAuth API as the workshop."""
from pathlib import Path
import argparse, json, urllib.request

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("episode",type=Path,help="Existing episode.json")
    parser.add_argument("--prompt",required=True)
    parser.add_argument("--model",default="gpt-6-astra")
    parser.add_argument("--effort",default="medium")
    args=parser.parse_args()
    episode=args.episode.resolve()
    spec=json.loads(episode.read_text(encoding="utf8"))
    payload=json.dumps({"prompt":args.prompt,"model":args.model,"effort":args.effort}).encode()
    request=urllib.request.Request("http://127.0.0.1:8766/api/generate",data=payload,
        headers={"Content-Type":"application/json","Origin":"http://127.0.0.1:8766"})
    with urllib.request.urlopen(request,timeout=190) as response: result=json.load(response)
    required={"hipL","hipR","elbowL","elbowR","shoulderL","shoulderR","neck"}
    if not required.issubset(result["rig"]["joints"]):
        raise ValueError("Video needs separate humanoid arms and legs; episode was not changed.")
    filename=f"character-{result['promptId']}.boxes"
    (episode.parent/filename).write_text(result["code"],encoding="utf8")
    spec["characterBoxes"]=filename
    spec["characterGeneration"]={key:result.get(key) for key in ("promptId","model","effort")}
    pending=episode.with_suffix(".pending.json")
    pending.write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding="utf8")
    pending.replace(episode)
    print(episode.parent/filename)

if __name__=="__main__":main()
