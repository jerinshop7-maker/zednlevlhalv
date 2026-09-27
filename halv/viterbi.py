#!/usr/bin/env python3
"""
Exact-ish reconstruction of the HALV signal: Viterbi over integer vertex values
using the forward renderer in halv/model.py.  (route item 7.1)

Run:  python3 halv/viterbi.py 700 860
"""
import sys, numpy as np
sys.path.insert(0,'halv')
from model import col
from PIL import Image
a=np.array(Image.open('cryptoHALV.png').convert('L')).astype(np.float64)/255.0
ROWS=np.arange(86,860)
def make_cost(lo,hi):
    def c(x,va,vb): return float(np.abs(a[86:860,x]-col(va,vb,rows=ROWS)).sum())
    return c
def viterbi(LO,HI,VMAX=12,win=3,step=1.0):
    cost=make_cost(LO,HI); n=HI-LO+1
    grid=np.arange(0,VMAX+1e-9,step)
    dp={g:0.0 for g in grid}
    arg=[{}]
    for i in range(n):
        x=LO+i; new={}; na={}
        for q in grid:
            best=None
            for p in dp:
                if abs(p-q)>2*win*step+1e-9: continue
                cc=dp[p]+cost(x,p,q)
                if best is None or cc<best[0]: best=(cc,p)
            if best: new[q]=best[0]; na[q]=best[1]
        dp=new; arg.append(na)
    q=min(dp,key=dp.get); tot=dp[q]
    seq=[0.0]*n; seq[n-1]=q
    for i in range(n-1,0,-1): seq[i-1]=arg[i+1][seq[i]]
    return seq,tot
if __name__=='__main__':
    LO=int(sys.argv[1]) if len(sys.argv)>1 else 700
    HI=int(sys.argv[2]) if len(sys.argv)>2 else 860
    s,tot=viterbi(LO,HI)
    print('x=%d..%d  total L1=%.2f  per-column mean = %.3f grey levels'%(LO,HI,tot,tot/(HI-LO+1)/774*255))
    for i in range(0,len(s),32):
        print('  x=%3d :'%(LO+i+1),' '.join('%3d'%round(v) for v in s[i:i+32]))
    np.save('halv/vit_%d_%d.npy'%(LO,HI),np.array(s))
