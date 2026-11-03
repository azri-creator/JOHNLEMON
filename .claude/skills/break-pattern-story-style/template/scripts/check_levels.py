import numpy as np, scipy.io.wavfile as w
def L(n):
    sr,x=w.read(f"audio/{n}.wav"); return x.astype(np.float64)/(2**31 if x.dtype==np.int32 else 32768), sr
v,sr=L("stem_voice"); m,_=L("stem_music"); s,_=L("stem_sfx"); mix,_=L("mix")
db=lambda x: 20*np.log10(np.sqrt((x**2).mean())+1e-9)
print("mix peak dB %.2f"%(20*np.log10(abs(mix).max())))
bad=0
for k in range(0,int(len(v)/sr*4)):   # 0.25 s windows
    a,b=int(k*0.25*sr),int((k+1)*0.25*sr)
    vv=db(v[a:b,0]); mm=db(m[a:b].mean(1)); ss=db(s[a:b].mean(1))
    if vv>-30:
        if mm-vv>-14 or ss-vv>-6:
            bad+=1; print(f"{k*0.25:6.2f}s voice {vv:6.1f} music {mm-vv:5.1f} sfx {ss-vv:5.1f}")
print("windows flagged (voice active & music within 14 dB or sfx within 6 dB of voice):",bad)
act=[];
for k in range(0,int(len(v)/sr*4)):
    a,b=int(k*0.25*sr),int((k+1)*0.25*sr)
    if db(v[a:b,0])>-30: act.append((db(m[a:b].mean(1))-db(v[a:b,0])))
print("music vs voice while speaking: median %.1f dB, p90 %.1f dB"%(np.median(act),np.percentile(act,90)))
