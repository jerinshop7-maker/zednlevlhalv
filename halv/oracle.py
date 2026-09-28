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
def ser(p): return (b'\x02' if p[1]%2==0 else b'\x03')+p[0].to_bytes(32,'big')
def b58(b):
    A='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    n=int.from_bytes(b,'big'); s=''
    while n: n,r=divmod(n,58); s=A[r]+s
    for c in b:
        if c==0: s='1'+s
        else: break
    return s
def b58c(b):
    return b58(b+hashlib.sha256(hashlib.sha256(b).digest()).digest()[:4])
def hash160(b): return hashlib.new('ripemd160',hashlib.sha256(b).digest()).digest()
TARGET='1crypto24HCr178iMcKd5iUi5D4rsg1nK'
H160='06c84797d1f468b9d5773a61c80073b344df7470'
def addr(k,comp=False):
    Q=mul(k); pub=(b'\x03' if comp else b'\x04')+Q[0].to_bytes(32,'big')+Q[1].to_bytes(32,'big') if not comp else ser(Q)
    return b58c(b'\x00'+hash160(pub))
def check(k):
    if not (0<k<N): return False
    # The target address may have been generated from either pubkey encoding.
    Q=mul(k)
    pub_u=b'\x04'+Q[0].to_bytes(32,'big')+Q[1].to_bytes(32,'big')
    return (b58c(b'\x00'+hash160(pub_u))==TARGET
            or b58c(b'\x00'+hash160(ser(Q)))==TARGET)

if __name__=='__main__':
    assert addr(1,comp=False)=='1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm'
    assert addr(1,comp=True)=='1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH'
    print('oracle controls passed (private key 1, compressed and uncompressed)')
