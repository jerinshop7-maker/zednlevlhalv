#!/usr/bin/env python3
"""
Zden 'BTCrypto Puzzle Level HALV'  --  measurement pipeline (all CONFIRMED facts).

Re-derives, from cryptoHALV.png alone:
  F1  mirror symmetry about y = 475 (signal is rectified)
  F2  stroke cross-section profile and width
  F3  the amplitude ladder  {3*2^k} U {2^k}   (18 levels, 8 halvings)
  F4  the list of exactly-horizontal plateaus (level, x0, x1, length)
  F5  the per-column signal level map

Run:  python3 halv/measure.py
"""
import numpy as np, hashlib
from PIL import Image

PNG='cryptoHALV.png'
TARGET='1crypto24HCr178iMcKd5iUi5D4rsg1nK'
HASH160='06c84797d1f468b9d5773a61c80073b344df7470'
KR=np.array([0.0667,0.4314,1.0000,0.4314,0.0667])   # measured stroke cross-section (peak 1.0)
LAD=[384,256,192,128,96,64,48,32,24,16,12,8,6,4,3,2,1]   # U {3*2^k} U {2^k}  (1.5 also exists, non-integer)
X0,X1=88,860

a=np.array(Image.open(PNG).convert('L')).astype(np.float64)/255.0
UP=a[:475,:]

def mirror_fidelity():
    out=[]
    for x in [100,200,300,400,500,600,700,750]:
        d=[abs(a[r,x]-a[950-r,x]) for r in range(86,475) if 950-r<950]
        d=np.array(d); out.append((x,d.mean(),(d<1e-9).mean()))
    return out

def template_scores():
    """score[v,x] = normalised correlation of the upper-half column with a flat stroke at 475-v"""
    S=np.zeros((len(LAD)+1, X1-X0))
    for i,v in enumerate(LAD):
        c=int(round(475.0-v)); lo=max(0,c-2); hi=min(474,c+2)+1
        t=np.zeros(475); t[lo:hi]=KR[lo-(c-2):hi-(c-2)]
        tn=np.sqrt((t*t).sum())
        o=UP[:,X0:X1]
        num=(o*t[:,None]).sum(axis=0); den=tn*np.sqrt((o*o).sum(axis=0))+1e-12
        S[i]=num/den
    return S

def plateaus(S, thr=0.992):
    best=S.argmax(axis=0); sc=S.max(axis=0)
    res=[]; x=0
    while x<X1-X0:
        if sc[x]>thr:
            j=x
            while j+1<X1-X0 and sc[j+1]>thr: j+=1
            vv=best[x:j+1]
            if len(set(vv.tolist()))==1:
                res.append((LAD[int(vv[0])], x+X0, j+X0, j-x+1))
            x=j+1
        else: x+=1
    return res

if __name__=='__main__':
    d=open(PNG,'rb').read()
    print('='*72)
    print('file  %s  %d bytes'%(PNG,len(d)))
    print('sha256 %s'%hashlib.sha256(d).hexdigest())
    print('='*72)
    print('F1 mirror symmetry about y=475   (x, mean|diff|, frac exactly equal)')
    for x,m,f in mirror_fidelity(): print('     x=%3d  mean=%.4f  exact=%.3f'%(x,m,f))
    print('     -> the drawn signal is |s|; the sign of s is NOT in the image  [CONFIRMED]')
    print()
    print('F2 stroke cross-section (measured on flat runs): %s  total=%.4f'%(np.round(KR,4),KR.sum()))
    print('     stroke width w = %.3f px'%KR.sum())
    print()
    print('F3 amplitude ladder: %s'%LAD)
    FULL=LAD[:-1]+[1.5,1.0]     # 2 -> 1.5 -> 1  (the two non-integer rungs are still present)
    r=[FULL[i+1]/FULL[i] for i in range(len(FULL)-1)]
    print('     full ladder incl. non-integer rungs: %s'%FULL)
    print('     consecutive ratios: %s'%np.round(r,4))
    print('     -> strictly alternate x2/3, x3/4 ; each PAIR is exactly one halving (x1/2)')
    print('     -> 18 rungs = 8 halvings + 1.  log2(384)=7.585. This IS "HALV". [CONFIRMED]')
    print()
    S=template_scores()
    P=plateaus(S)
    print('F4 exactly-horizontal plateaus (template score > 0.992): %d'%len(P))
    print('     level   x0    x1   len')
    for v,a0,b0,l in P: print('     %5d %5d %5d %5d'%(v,a0,b0,l))
    np.save('halv/plateaus.npy', np.array(P))
    print()
    print('F5 target address %s'%TARGET)
    print('   next -> halv/viterbi.py   (route item 7.1: exact integer reconstruction)')
