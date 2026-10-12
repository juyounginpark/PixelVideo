"""Place labels near their subjects while protecting supplied face/action bounds."""
def intersects(a,b,padding=12):
    return a[0]<b[2]+padding and a[2]>b[0]-padding and a[1]<b[3]+padding and a[3]>b[1]-padding

def place_label(anchor,size,protected=(),safe=(95,300,900,1240)):
    x,y=anchor[:2];w,h=size
    if w>safe[2]-safe[0] or h>safe[3]-safe[1]:raise ValueError('Label exceeds safe region; shorten text')
    candidates=((x+45,y-h-90),(x-w-45,y-h-90),(x+45,y+50),(x-w-45,y+50),
                (safe[0],safe[1]),(safe[2]-w,safe[1]),(safe[0],safe[3]-h),(safe[2]-w,safe[3]-h))
    for cx,cy in candidates:
        cx=max(safe[0],min(safe[2]-w,cx));cy=max(safe[1],min(safe[3]-h,cy));rect=(cx,cy,cx+w,cy+h)
        if not any(intersects(rect,b) for b in protected):return rect
    raise ValueError('No unobstructed label position; omit panel or reframe subject')
