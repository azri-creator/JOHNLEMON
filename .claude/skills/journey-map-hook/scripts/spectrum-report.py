import wave,numpy as np,sys
def spec(p,thr):
    w=wave.open(p);sr=w.getframerate();x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
    n=4096;win=np.hanning(n);acc=np.zeros(n//2+1);c=0
    for i in range(0,len(x)-n,n):
        seg=x[i:i+n]
        if np.sqrt(np.mean(seg**2))>thr: acc+=np.abs(np.fft.rfft(seg*win))**2;c+=1
    f=np.fft.rfftfreq(n,1/sr);db=10*np.log10(acc/c+1e-12)
    return [db[(f>=lo)&(f<hi)].mean() for lo,hi in [(80,200),(200,500),(500,1000),(1000,2000),(2000,4000),(4000,6000),(6000,8000),(8000,12000)]]
a=spec(sys.argv[1],0.03); b=spec(sys.argv[2],0.03)
print("band       before  after (rel to 200-500)")
for n,x,y in zip(["80-200","200-500","500-1k","1-2k","2-4k","4-6k","6-8k","8-12k"],a,b): print(f"{n:8s} {x-a[1]:6.1f} {y-b[1]:6.1f}")
