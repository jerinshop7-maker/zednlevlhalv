import numpy as np
from PIL import Image
img=np.array(Image.open('cryptoHALV.png').convert('L')).astype(float)/255.0
H,W=img.shape
M_meas=img[:476,:].sum(axis=0)          # column mass, upper half
# subpixel top edge of stroke -> measured "A"
A_meas=np.full(W,np.nan)
for x in range(88,872):
    col=img[:476,x]
    if col.sum()<0.6: continue
    idx=np.where(col>0)[0]; c=np.cumsum(col[idx])
    k=np.searchsorted(c,0.75)
    A_meas[x]=475.0-(idx[0]+(k-1)+(0.75-(c[k-1] if k>0 else 0)))
OFF=92.0; N=256; CY=475.0
def colfeat(v,c0,c1):
    """maxv, tv for columns c0..c1-1  (upper half: y=CY-v)"""
    X=np.arange(c0,c1)+0.5            # column centres
    maxv=np.zeros(c1-c0); tv=np.zeros(c1-c0)
    pts=OFF+3*np.arange(N)
    for k in range(N-1):
        x1,x2=pts[k],pts[k+1]
        lo=max(x1,X[0]); hi=min(x2,X[-1])
        if hi<lo: continue
        s1=(max(lo,x1-0.5)-x1)/3.0; s2=(min(hi,x1+0.5)-x1)/3.0   # within [0,1]
        # columns spanned
        ca=int(np.floor(max(lo,X[0])-0.5)); cb=int(np.floor(min(hi,X[-1])-0.5))
        for c in range(ca,cb+1):
            if c<c0 or c>=c1: continue
            a0=max(c-0.5,x1); a1=min(c+0.5,x2)
            if a1<a0: continue
            t0=(a0-x1)/3.0; t1=(a1-x1)/3.0
            v0=v[k]+(v[k+1]-v[k])*t0; v1=v[k]+(v[k+1]-v[k])*t1
            maxv[c-c0]=max(maxv[c-c0],v0,v1)
            tv[c-c0]+=abs(v1-v0)
    return maxv,tv
w=1.4784; r=0.7392
def local_cost(v,k,cols=range(86,872)):
    pass
# global cost function (vectorised over all columns) but computed incrementally
def cost_cols(v,c0,c1):
    maxv,tv=colfeat(v,c0,c1)
    Ap=CY-maxv-r
    Mp=w*(1.0+tv)
    d=A_meas[c0:c1]
    ok=~np.isnan(d)
    e1=(Ap[ok]-d[ok])**2
    e2=(Mp[ok]-M_meas[c0:c1][ok])**2
    return float((e1*1.0+e2*4.0).sum())
v=np.zeros(N)
for k in range(N):
    x=int(round(OFF+3*k)); v[k]=max(0.0,(A_meas[x] if x<W else 0)+r)
np.save('v0.npy',v)
print('init cost',round(cost_cols(v,88,872),1))
import time
t0=time.time()
for it in range(6):
    for k in range(N):
        x=int(round(OFF+3*k))
        hi=int(min(400,(A_meas[x] if x<W else 0)+r+3))
        c0=max(88,int(round(OFF+3*max(0,k-2)))-3); c1=min(872,int(round(OFF+3*min(N-1,k+2)))+4)
        best=(1e18,v[k])
        for cand in range(0,hi+1):
            old=v[k]; v[k]=cand
            e=cost_cols(v,c0,c1)
            if e<best[0]: best=(e,float(cand))
            v[k]=old
        v[k]=best[1]
    print('iter',it,'cost',round(cost_cols(v,88,872),1),'t=%.0fs'%(time.time()-t0))
    np.save(f'vf_{it}.npy',v)
print('v=',[int(x) for x in v])
