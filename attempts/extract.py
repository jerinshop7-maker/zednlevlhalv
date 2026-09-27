import numpy as np
from PIL import Image
a=np.array(Image.open('cryptoHALV.png').convert('L')).astype(float)
H,W=a.shape
M=a[:476,:].sum(axis=0)/255.0
w=1.4784
# subpixel top boundary
def topedge(frac=0.75):
    top=np.full(W,np.nan)
    for x in range(88,872):
        col=a[:,x]
        if col.sum()/255.0<0.6: continue
        idx=np.where(col>0)[0]; c=np.cumsum(col[idx])/255.0
        k=np.searchsorted(c,frac)
        top[x]= idx[0]+(k-1)+(frac-(c[k-1] if k>0 else 0))
    return 475.0-top
A=topedge()
# grid
OFF=92.0
xs=OFF+3*np.arange(256)
# |dv| per segment, half-column weighted
D=np.zeros(255)
for k in range(255):
    x0=int(round(OFF+3*k))
    D[k]=(0.5*M[x0]+M[x0+1]+M[x0+2]+0.5*M[x0+3])/w-3.0
np.save('D2.npy',D); np.save('A4.npy',A)
print('D2 first 40:',np.round(D[:40],2))
print('frac parts:',np.round(np.abs(D-np.round(D)),2)[:40])
print('A at grid (f, first 40):',[None if np.isnan(A[int(round(v))]) else round(A[int(round(v))],1) for v in xs[:40]])
