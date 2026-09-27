import numpy as np
A=np.load('A4.npy'); D=np.load('D2.npy')
OFF=92.0
def Am(k):
    x=int(round(OFF+3*k)); return A[x] if x<950 else 0.0
def predA(v,k):
    n=len(v); c=v[-1] if k>=n else v[k]
    if k<n-1:
        c=max(c, v[k]+(v[k+1]-v[k])*(0.5/3.0))
    if k>=1:
        c=max(c, v[k]+(v[k-1]-v[k])*(0.5/3.0))
    return c-0.74
v0=int(round(Am(0)+0.74))
beam=[(0.0,[v0])]
for k in range(255):
    d0=D[k]; base=int(round(d0))
    cands=sorted({max(0,base-2),max(0,base-1),base,base+1,base+2})
    nb=[]
    for sc,path in beam:
        pv=path[-1]
        for d in cands:
            for s in (1,-1):
                nv=pv+s*d
                if nv<0: continue
                p2=path+[nv]
                nb.append((sc+(predA(p2,k+1)-Am(k+1))**2, p2))
    nb.sort(key=lambda t:t[0])
    beam=nb[:60]
best=beam[0]; v=np.array(best[1],dtype=float)
print('score',round(best[0],2))
print('v =',[int(x) for x in v])
np.save('v_rec.npy',v)
print('resid:',[round(predA(v,k)-Am(k),1) for k in range(256)])
