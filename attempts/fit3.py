import numpy as np
from PIL import Image
img=np.array(Image.open('cryptoHALV.png').convert('L')).astype(float)/255.0
H,W=img.shape
M=img[:476,:].sum(axis=0)
# topmost row with coverage -> T(x); and refined subpixel via 0.5 coverage
def topcov(frac):
    T=np.full(W,np.nan)
    for x in range(88,872):
        col=img[:476,x]
        if col.sum()<0.6: continue
        idx=np.where(col>0)[0]; c=np.cumsum(col[idx])
        k=np.searchsorted(c,frac)
        T[x]=475.0-(idx[0]+(k-1)+(frac-(c[k-1] if k>0 else 0)))
    return T
T75=topcov(0.75); T25=topcov(0.25)
OFF=92.0; N=256; CY=475.0
PTS=OFF+3*np.arange(N)
def colfeat(v,c0,c1):
    maxv=np.zeros(c1-c0); tv=np.zeros(c1-c0)
    for k in range(N-1):
        x1,x2=PTS[k],PTS[k+1]
        if x2< c0-0.5 or x1> c1-0.5: continue
        ca=max(c0,int(np.floor(x1-0.5))); cb=min(c1-1,int(np.floor(x2-0.5)))
        for c in range(ca,cb+1):
            a0=max(c-0.5,x1); a1=min(c+0.5,x2)
            if a1<a0: continue
            t0=(a0-x1)/3.0; t1=(a1-x1)/3.0
            v0=v[k]+(v[k+1]-v[k])*t0; v1=v[k]+(v[k+1]-v[k])*t1
            if v0>maxv[c-c0]: maxv[c-c0]=v0
            if v1>maxv[c-c0]: maxv[c-c0]=v1
            tv[c-c0]+=abs(v1-v0)
    return maxv,tv
def cost(v,c0,c1,w,r,wT,wM):
    maxv,tv=colfeat(v,c0,c1)
    Tp=CY-maxv-r
    t75=T75[c0:c1]; t25=T25[c0:c1]; m=M[c0:c1]
    ok=~np.isnan(t75)
    e=((Tp[ok]-t75[ok])**2 + ((Tp[ok]-r*0.5)-t25[ok])**2)*wT + (w*(1+tv[ok])-m[ok])**2*wM
    return float(e.sum())
if __name__=='__main__':
    K0,K1=118,256
    c0=int(round(OFF+3*(K0-2)))-3; c1=min(872,int(round(OFF+3*(K1-1)))+4)
    best=None
    for w in np.arange(1.40,1.56,0.01):
        for r in np.arange(0.55,0.95,0.02):
            v=np.zeros(N)
            for k in range(K0,K1):
                x=int(round(OFF+3*k)); v[k]=max(0.0,(T75[x] if x<W else 0)+r)
            e=cost(v,c0,c1,w,r,1.0,25.0)
            if best is None or e<best[0]: best=(e,w,r)
    e,w,r=best
    print('calib: cost=%.1f w=%.3f r=%.3f'%(e,w,r))
    v=np.zeros(N)
    for k in range(K0,K1):
        x=int(round(OFF+3*k)); v[k]=max(0.0,(T75[x] if x<W else 0)+r)
    for it in range(8):
        for k in range(K0,K1):
            cc0=max(c0,int(round(OFF+3*(k-2)))-3); cc1=min(c1,int(round(OFF+3*(k+2)))+4)
            bst=(1e18,v[k])
            for step in (1.0,0.5,0.25):
                pass
            for cand in np.arange(0,max(30,v[k]+4),0.25):
                old=v[k]; v[k]=cand
                ee=cost(v,cc0,cc1,w,r,1.0,25.0)
                if ee<bst[0]: bst=(ee,cand)
                v[k]=old
            v[k]=bst[1]
        print('it',it,'cost=%.2f'%cost(v,c0,c1,w,r,1.0,25.0))
    np.save('vfine.npy',v); np.save('calib.npy',np.array([w,r]))
    print('v[118:256] =',[round(float(x),2) for x in v[118:]])
