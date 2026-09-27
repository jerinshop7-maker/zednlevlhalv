import hashlib
P=2**256-2**32-977
N=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy=0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
def inv(a,m=P): return pow(a,m-2,m)
def add(p,q):
    if p is None: return q
    if q is None: return p
    if p[0]==q[0] and (p[1]+q[1])%P==0: return None
    if p==q: l=(3*p[0]*p[0])*inv(2*p[1])%P
    else: l=(q[1]-p[1])*inv(q[0]-p[0])%P
    x=(l*l-p[0]-q[0])%P
    return (x,(l*(p[0]-x)-p[1])%P)
def mul(k,p=(Gx,Gy)):
    r=None
    while k:
        if k&1: r=add(r,p)
        p=add(p,p); k>>=1
    return r
def ser(p):
    return (b'\x02' if p[1]%2==0 else b'\x03')+p[0].to_bytes(32,'big')
def b58(b):
    A='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    n=int.from_bytes(b,'big'); s=''
    while n: n,r=divmod(n,58); s=A[r]+s
    for c in b:
        if c==0: s='1'+s
        else: break
    return s
def b58c(b):
    chk=hashlib.sha256(hashlib.sha256(b).digest()).digest()[:4]
    return b58(b+chk)
def hash160(b): return hashlib.new('ripemd160',hashlib.sha256(b).digest()).digest()
def addr_from_priv(k):
    Q=mul(k)
    pub=ser(Q)
    h=hash160(pub)
    return b58c(b'\x00'+h), Q
def wif(k,comp=False):
    kb=k.to_bytes(32,'big')
    if comp: kb=b'\x01'+kb
    return b58c(b'\x80'+kb+b'\x01')
TARGET='1crypto24HCr178iMcKd5iUi5D4rsg1nK'
if __name__=='__main__':
    import sys
    d=open('cryptoHALV.png','rb').read()
    cands={}
    cands['sha256(file)']=hashlib.sha256(d).digest()
    cands['sha256d(file)']=hashlib.sha256(hashlib.sha256(d).digest()).digest()
    cands['sha1(file)']=hashlib.sha1(d).digest()
    cands['md5(file)']=hashlib.md5(d).digest()
    cands['sha512(file)']=hashlib.sha512(d).digest()
    cands['sha256(hex-of-sha256)']=hashlib.sha256(hashlib.sha256(d).hexdigest().encode()).digest()
    for name,k in cands.items():
        kk=int.from_bytes(k[:32],'big')
        if kk==0 or kk>=N: continue
        a,_=addr_from_priv(kk)
        print(f"{name:28s} {a}  {'*** MATCH ***' if a==TARGET else ''}")
