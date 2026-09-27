import numpy as np
from PIL import Image
img=np.array(Image.open('cryptoHALV.png').convert('L')).astype(float)/255.0
H,W=img.shape
SS=4                      # supersampling
w_stroke=1.4784           # measured stroke width
r=w_stroke/2.0
OFF=92.0; N=256; CY=475.0
# precompute subsample offsets
offs=(np.arange(SS)+0.5)/SS-0.5
def render_win(v,i0,i1,c0,c1,r0,r1):
    """render columns c0..c1-1, rows r0..r1-1 for polyline v (full 256) """
    out=np.zeros((r1-r0,c1-c0))
    xs=np.arange(c0,c1)+0.5
    ys=np.arange(r0,r1)+0.5
    X=xs[None,:]+0.0     # placeholder
    # gather polyline points involved
    k0=max(0,i0-1); k1=min(N-1,i1+1)
    px=OFF+3*np.arange(k0,k1+1)
    py=CY-v[k0:k1+1]
    for oy in offs:
        for ox in offs:
            Xs=xs[None,:]+ox       # (1,nx)
            Ys=ys[:,None]+oy        # (ny,1)
            d=np.full((len(ys),len(xs)),1e9)
            for t in range(len(px)-1):
                x1,y1=px[t],py[t]; x2,y2=px[t+1],py[t+1]
                dx=x2-x1; dy=y2-y1
                L2=dx*dx+dy*dy
                if L2==0: continue
                s=((Xs-x1)*dx+(Ys-y1)*dy)/L2
                s=np.clip(s,0,1)
                d=np.minimum(d,np.hypot(Xs-(x1+s*dx),Ys-(y1+s*dy)))
            out+= (d<=r)
    return out/(SS*SS)
def win_err(v,i0,i1):
    c0=int(round(OFF+3*i0))-3; c1=int(round(OFF+3*i1))+4
    c0=max(88,c0); c1=min(872,c1)
    seg=v[max(0,i0-1):min(N,i1+2)]
    if len(seg)==0: return 0.0,None
    ymax=CY-min(seg); ymin=CY-max(seg)
    r0=max(0,int(ymin-r-3)); r1=min(478,int(ymax+r+4))
    if r1<=r0: return 0.0,None
    pred=render_win(v,i0,i1,c0,c1,r0,r1)
    obs=img[r0:r1,c0:c1]
    return float(((pred-obs)**2).sum()*2), (c0,c1,r0,r1)
if __name__=='__main__':
    A=np.load('A4.npy')
    v=np.zeros(N)
    for k in range(N):
        x=int(round(OFF+3*k)); v[k]=max(0.0,(A[x] if x<W else 0)+0.74)
    # refine with local coordinate descent on the RIGHT half (no clipping) then all
    import itertools
    for it in range(4):
        for k in range(N):
            base=v[max(0,k-2):min(N,k+3)].max()
            best=(1e18,v[k])
            cand=set()
            for c in range(0,int(min(400,base+8))+1):
                cand.add(float(c))
            for c in sorted(cand):
                old=v[k]; v[k]=c
                e,_=win_err(v,k-1,k+1)
                if e<best[0]: best=(e,c)
                v[k]=old
            v[k]=best[1]
        np.save(f'vfit_{it}.npy',v)
        print('iter',it,'v=',[int(x) for x in v])
