import numpy as np, time
from PIL import Image
img=np.array(Image.open('cryptoHALV.png').convert('L')).astype(float)/255.0
SS=8; OFF=92.0; N=256; CY=475.0
off=(np.arange(SS)+0.5)/SS-0.5
def render_cols(v,k0,k1,c0,c1,r0,r1,r):
    ny=r1-r0; nx=c1-c0
    xs=np.arange(c0,c1)+0.5
    ys=np.arange(r0,r1)+0.5
    X=np.broadcast_to((np.repeat(xs,SS)[None,:]+np.tile(off,nx)[None,:]),(ny*SS,nx*SS))
    Y=np.broadcast_to((np.repeat(ys,SS)[:,None]+np.tile(off,ny)[:,None]),(ny*SS,nx*SS))
    acc=np.zeros((ny,nx))
    for k in range(max(0,k0-1),min(N-1,k1)+1):
        x1=OFF+3*k; y1=CY-v[k]; x2=OFF+3*(k+1); y2=CY-v[k+1]
        dx=x2-x1; dy=y2-y1; L2=dx*dx+dy*dy
        t=np.clip(((X-x1)*dx+(Y-y1)*dy)/L2,0,1)
        d=np.hypot(X-(x1+t*dx), Y-(y1+t*dy))
        acc+=((d<=r).reshape(ny,SS,nx,SS).sum(axis=(1,3)))
    return acc/(SS*SS)
def err(v,k0,k1,c0,c1,r0,r1,r):
    p=render_cols(v,k0,k1,c0,c1,r0,r1,r)
    o=img[r0:r1,c0:c1]
    return float(((p-o)**2).sum())
def fit(K0,K1,w,r,iters=4,step=0.5,seed=None):
    v=np.zeros(N)
    if seed is not None: v=v.copy(); v[:]=seed
    else:
        for k in range(N):
            x=int(round(OFF+3*k))
            v[k]=max(0.0,475.0-(img[:476,x][np.where(img[:476,x]>0)[0][0]] if (x<950 and img[:476,x].sum()>0.5) else 475)-r)
    v=np.round(v/0.5)*0.5
    for it in range(iters):
        for k in range(K0,K1):
            c0=max(0,int(round(OFF+3*k))-4); c1=min(950,int(round(OFF+3*k))+8)
            seg=v[max(0,k-2):min(N,k+3)]
            r0=max(0,int(CY-seg.max()-r-4)); r1=min(478,int(CY-seg.min()+r+5))
            if r1-r0<3: continue
            bst=(1e18,v[k]); old=v[k]
            hi=min(48.0,old+3*step)
            for cand in np.arange(0,hi+1e-9,step):
                v[k]=cand
                e=err(v,k-1,k+1,c0,c1,r0,r1,r)
                if e<bst[0]: bst=(e,cand)
            v[k]=bst[1]
    return v
if __name__=='__main__':
    t0=time.time()
    K0,K1=96,256
    best=None
    for r in (0.60,0.68,0.74,0.80,0.86):
        vv=fit(K0,K1,None,r,iters=2,step=1.0)
        c0=int(round(OFF+3*K0))-4; c1=int(round(OFF+3*(K1-1)))+8
        r0=0; r1=478
        e=err(vv,K0-2,K1-1,c0,c1,r0,r1,r)*2
        print('r=%.2f  err=%.5f  (%.0fs)'%(r,e,time.time()-t0))
        if best is None or e<best[0]: best=(e,r,vv.copy())
    e,r,vv=best
    print('best r',r)
    vv=fit(K0,K1,None,r,iters=4,step=0.5,seed=vv)
    np.save('v4.npy',vv); np.save('r4.npy',np.array([r]))
    print('total %.0fs'%(time.time()-t0))
    print('v[96:] =',[round(float(x),2) for x in vv[96:]])
