import numpy as np
KR=np.array([0.0667,0.4314,1.0000,0.4314,0.0667])
M=len(KR)//2; TAPS=np.arange(-M,M+1)
_XC=np.concatenate((TAPS-0.5,[TAPS[-1]+0.5])); _FP=np.concatenate(([0.0],np.cumsum(KR)))
TOT=KR.sum()
def KRc(t): return np.interp(t,_XC,_FP,left=0.0,right=TOT)
def _seg(ya,yb,rows,gq=(0.1,0.3,0.5,0.7,0.9)):
    m=yb-ya; c=1.0/np.sqrt(1.0+m*m); acc=np.zeros(len(rows))
    for q in gq:
        yl=ya+m*q
        acc+=(KRc((rows+0.5-yl)*c)-KRc((rows-0.5-yl)*c))/c
    return acc/len(gq)
def _disc(yc,rows): return np.interp(np.abs(rows-yc),TAPS,KR,left=0.0,right=0.0)

def col(va,vb,mirror=True,rows=None):
    if rows is None: rows=np.arange(0,950)
    ya=475.0-va; yb=475.0-vb
    up=np.maximum(np.maximum(_seg(ya,yb,rows),_disc(ya,rows)),_disc(yb,rows))
    np.clip(up,0,1,out=up)
    if not mirror: return up
    A,B=950.0-ya,950.0-yb
    lo=np.maximum(np.maximum(_seg(A,B,rows),_disc(A,rows)),_disc(B,rows))
    np.clip(lo,0,1,out=lo)
    return np.maximum(up,lo)
