#!/usr/bin/env python3
import sys, itertools, hashlib
import numpy as np
from PIL import Image
P = 2**256 - 2**32 - 977
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
TARGET = "1crypto24HCr178iMcKd5iUi5D4rsg1nK"
def inv(a): return pow(a, P-2, P)
def add(a,b):
    if a is None: return b
    if b is None: return a
    if a[0]==b[0] and (a[1]+b[1])%P==0: return None
    lam=(3*a[0]*a[0]*inv(2*a[1]))%P if a==b else ((b[1]-a[1])*inv(b[0]-a[0]))%P
    x=(lam*lam-a[0]-b[0])%P
    return x,(lam*(a[0]-x)-a[1])%P
def mul(k,p=(GX,GY)):
    r=None
    while k:
        if k&1: r=add(r,p)
        p=add(p,p); k>>=1
    return r
B58="123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def b58c(raw):
    n=int.from_bytes(raw,"big"); out=""
    while n: n,r=divmod(n,58); out=B58[r]+out
    z=0
    for c in raw:
        if c==0: z+=1
        else: break
    return "1"*z+out
def h160(b): return hashlib.new('ripemd160',hashlib.sha256(b).digest()).digest()
def p2pkh(k,comp):
    Q=mul(k)
    pub=(b"\x02" if Q[1]%2==0 else b"\x03")+Q[0].to_bytes(32,"big") if comp else b"\x04"+Q[0].to_bytes(32,"big")+Q[1].to_bytes(32,"big")
    return b58c(b"\x00"+h160(pub))
def amplitude_trace(path):
    a=np.asarray(Image.open(path).convert("L"),dtype=np.float64)/255.0
    if a.shape!=(950,950): raise ValueError("expected 950x950, got %s"%(a.shape,))
    v=np.zeros(950)
    for x in range(88,861):
        col=a[:475,x]; ys=np.flatnonzero(col>0.04)
        if len(ys)==0: v[x]=0.0; continue
        m=col[ys].max(); keep=ys[col[ys]>=max(0.04,0.20*m)]
        w=col[keep]; yc=np.sum(keep*w)/np.sum(w); v[x]=max(0.0,475.0-yc)
    return v
def recover_q(v,x0=90):
    best=None
    for phase in range(6):
        q=[]; err=0.0; ok=True
        for n in range(128):
            xc=x0+phase+6*n+2.5; xi=int(round(xc))
            if xi<91 or xi>=859: ok=False; break
            b=min(7,(xi-x0)//96); s=128>>b
            lo=x0+phase+6*n; hi=lo+6
            lo=max(91,lo); hi=min(859,hi)
            vals=v[lo:hi]; amp=float(np.median(vals))/s
            qq=int(np.clip(round(amp),0,3))
            err+=float(np.mean((vals/s-qq)**2)); q.append(qq)
        if ok and (best is None or err<best[0]): best=(err,phase,q)
    return best
def bits_for(q,perm): return "".join(format(perm[x],"02b") for x in q)
def check_bits(bits):
    seen=set()
    for reverse in (False,True):
        s=bits[::-1] if reverse else bits
        for pr in (False,True):
            t="".join(s[i:i+2][::-1] for i in range(0,256,2)) if pr else s
            for br in (False,True):
                u="".join(t[i:i+8][::-1] for i in range(0,256,8)) if br else t
                for bo in (False,True):
                    b="".join(u[i:i+8] for i in range(248,-1,-8)) if bo else u
                    k=int(b,2)
                    if 0<k<N and k not in seen:
                        seen.add(k); yield k
def main():
    path=sys.argv[1] if len(sys.argv)>1 else "cryptoHALV.png"
    v=amplitude_trace(path); best=recover_q(v)
    err,phase,q=best
    print("measurement phase=%d  SSE=%.6f"%(phase,err))
    print("q =","".join(map(str,q)))
    print("blocks:")
    for b in range(8): print("  %d: %s"%(b,"".join(map(str,q[16*b:16*(b+1)]))))
    np.save('q4_recovered.npy',np.array(q)); np.save('q4_trace.npy',v)
    hits=0
    for perm in itertools.permutations(range(4)):
        bits=bits_for(q,perm)
        for k in check_bits(bits):
            for comp in (False,True):
                hits+=1
                if p2pkh(k,comp)==TARGET:
                    print("\n*** SOLVED ***"); print("privkey =","%064x"%k)
                    print("mapping =",perm,"compressed =",comp); return 0
    print("\nNo exact target match among %d decoded candidates."%hits)
    return 1
if __name__=="__main__": raise SystemExit(main())
