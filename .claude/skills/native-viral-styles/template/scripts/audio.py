# Voice-aware music bed + fully unique synthesized SFX (no sample is reused)
import numpy as np, subprocess, wave
from scipy import signal
SR=48000; DUR=45.3; n=int(DUR*SR)
def ff(a): subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y"]+a,check=True)
def rd(p):
    w=wave.open(p);ch=w.getnchannels();d=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
    return d.reshape(-1,ch) if ch>1 else d
def wr(p,x):
    x=np.clip(x,-1,1)
    if x.ndim==1: x=np.stack([x,x],1)
    w=wave.open(p,'wb');w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((x*32767).astype(np.int16).tobytes());w.close()
ff(["-i","hf/assets/src/main.mov","-vn","-ac","1","-ar",str(SR),"hf/build/voice48.wav"])
voice=rd("hf/build/voice48.wav");voice=np.pad(voice,(0,max(0,n-len(voice))))[:n]
def env(x,win=.05):k=int(win*SR);return np.sqrt(np.convolve(x**2,np.ones(k)/k,mode='same')+1e-12)
venv=env(voice);vo_rms=np.sqrt(np.mean(voice[venv>10**(-45/20)]**2))
# ---------------- music ----------------
ff(["-i","hf/assets/src/music_full.m4a","-ac","2","-ar",str(SR),"hf/build/music_full.wav"])
m=rd("hf/build/music_full.wav");mono=m.mean(1)
rms=np.array([np.sqrt(np.mean(mono[i*SR:(i+1)*SR]**2)) for i in range(len(mono)//SR)])
need=int(np.ceil(DUR*.75))+2;best=None
for s0 in range(70,len(rms)-need):
    w=rms[s0:s0+need];sc=np.std(np.log(w+1e-6))+(0 if w.mean()>.04 else 1)
    if best is None or sc<best[0]:best=(sc,s0)
s0=best[1];print("music window",s0)
ff(["-ss",str(s0),"-t",str(need),"-i","hf/build/music_full.wav","-af","atempo=0.75,lowpass=f=3800,highpass=f=40","hf/build/music_slow.wav"])
ms=rd("hf/build/music_slow.wav");ms=np.pad(ms,((0,max(0,n-len(ms))),(0,0)))[:n]
g=(vo_rms*10**(-20/20))/np.sqrt(np.mean(ms.mean(1)**2))
act=(venv>10**(-42/20)).astype(np.float32);a_=np.exp(-1/(.03*SR));r_=np.exp(-1/(.28*SR));smv=np.zeros_like(act);c=0.
for i in range(n):
    c=a_*c+(1-a_)*act[i] if act[i]>c else r_*c+(1-r_)*act[i];smv[i]=c
gain=g*(10**(2/20)-(10**(2/20)-10**(-2/20))*smv)
fade=np.ones(n);fi=int(.8*SR);fo=int(1.8*SR);fade[:fi]=np.linspace(0,1,fi)**2;fade[-fo:]=np.linspace(1,0,fo)**2
# dropout on "Tak ada." (41.18) -> back for CTA
t=np.arange(n)/SR
drop=np.ones(n);drop[(t>=41.12)&(t<41.18)]=np.linspace(1,0,int(.06*SR)+1)[:np.sum((t>=41.12)&(t<41.18))]
drop[(t>=41.18)&(t<42.3)]=0;mk=(t>=42.3)&(t<42.9);drop[mk]=np.linspace(0,1,mk.sum())**2
music=ms*(gain*fade*drop)[:,None]
wr("hf/assets/audio/music.wav",music)
# ---------------- SFX: every event synthesized with its own seed/params ----------------
def T(d):return np.arange(int(d*SR))/SR
def sos(kind,f,order=2):return signal.butter(order,f,kind,fs=SR,output='sos')
def bp(x,lo,hi):return signal.sosfilt(sos('band',[max(30,lo),min(SR/2-200,hi)]),x)
def lp(x,f):return signal.sosfilt(sos('low',min(f,SR/2-200)),x)
def hp(x,f):return signal.sosfilt(sos('high',max(20,f)),x)
def nz(R,d):return R.standard_normal(int(d*SR)).astype(np.float32)
def nrm(x):return (x/(np.max(np.abs(x))+1e-9)).astype(np.float32)
def adsr(N,a,dcy,sh=1.):
    t=np.linspace(0,1,N);return np.minimum(t/max(a,1e-4),1)*np.exp(-np.maximum(t-a,0)*dcy)**sh
def sweep(R,d,f0,f1,q=.35,att=.3,dcy=3.):
    x=nz(R,d);N=len(x);out=np.zeros_like(x);B=28;bl=max(1,N//B)
    for b in range(B):
        f=f0*(f1/f0)**(b/(B-1));seg=bp(x[b*bl:(b+1)*bl+bl//2],f*(1-q),f*(1+q))[:bl];out[b*bl:b*bl+len(seg)]=seg
    return nrm(out*adsr(N,att,dcy))
def tone(f,d,dec,harm=((1,1),),fm=0,fmr=2.0,glide=1.0):
    t=T(d);ph=2*np.pi*np.cumsum(f*(glide**(t/d)))/SR;x=sum(a*np.sin(h*ph+fm*np.sin(2*np.pi*f*fmr*t)) for h,a in harm);return nrm(x*np.exp(-t*dec))
lib={}
def S(name,R):
    k=name
    if k=='boot':
        t=T(1.3);x=.8*np.sin(2*np.pi*(38+20*t)*t)*np.minimum(t/.5,1)*np.exp(-t*2)+.35*hp(nz(R,1.3),6000)*np.exp(-t*4)+.3*tone(1760*R.uniform(.98,1.02),1.3,3.5,((1,1),(2,.3)))
        return nrm(x)
    if k=='tink':return tone(R.uniform(2400,2800),.5,9,((1,1),(2.76,.4),(5.4,.15)))
    if k=='swish_up':return sweep(R,R.uniform(.3,.42),R.uniform(500,800),R.uniform(3500,5200),.4,.55,3)
    if k=='swish_dn':return sweep(R,R.uniform(.3,.42),R.uniform(4000,5200),R.uniform(500,800),.4,.15,3)
    if k=='key':
        d=.035;x=hp(nz(R,d),R.uniform(1800,3500))*np.exp(-T(d)*R.uniform(120,220))+.4*tone(R.uniform(900,1500),d,160);return nrm(x)
    if k=='zoom_in':
        t=T(.75);wh=np.sin(2*np.pi*np.cumsum(220+900*(t/.75)**1.6)/SR)*.35*(t/.75);x=wh+sweep(R,.75,400,4200,.3,.7,2.5)*.8;return nrm(x*np.minimum(t/.05,1))
    if k=='zoom_out':
        t=T(.7);wh=np.sin(2*np.pi*np.cumsum(1100-850*(t/.7)**.7)/SR)*.35*(1-t/.7);x=wh+sweep(R,.7,4200,350,.3,.15,2.5)*.8;return nrm(x)
    if k=='ping':
        f=R.uniform(1100,1500);return tone(f,.55,7,((1,1),(1.5,.5),(2,.25)))
    if k=='slide':return sweep(R,.35,R.uniform(300,500),R.uniform(1600,2400),.5,.4,4)
    if k=='pop':
        f=R.uniform(500,1500);t=T(.11);x=np.sin(2*np.pi*f*(1+.7*np.exp(-t*55))*t)*np.exp(-t*R.uniform(35,60));return nrm(x)
    if k=='slam':
        t=T(.9);x=np.sin(2*np.pi*(48+120*np.exp(-t*16))*t)*np.exp(-t*5)+.4*lp(nz(R,.9),900)*np.exp(-t*12)+.25*hp(nz(R,.9),7000)*np.exp(-t*6);return nrm(x)
    if k=='rewind':
        t=T(1.75);car=np.sin(2*np.pi*np.cumsum(2400*(1-.75*t/1.75)+180*np.sin(2*np.pi*7*t))/SR);x=car*.4+bp(nz(R,1.75),900,5000)*.6;return nrm(x*np.minimum(t/.1,1)*np.exp(-t*.8))
    if k=='bell':return tone(R.uniform(780,800),1.2,3.2,((1,1),(2.0,.5),(3.01,.3),(4.17,.15)))
    if k=='check':return tone(R.uniform(1000,1700),.35,11,((1,1),(3,.2)),fm=.6,fmr=R.uniform(1.4,2.2))
    if k=='riser':
        t=T(3.3);x=sweep(R,3.3,180,3600,.5,.98,.2)*.6+.4*np.sin(2*np.pi*np.cumsum(90+300*(t/3.3)**2)/SR)*(t/3.3)**1.5;return nrm(x)
    if k=='boom':
        t=T(1.4);x=np.sin(2*np.pi*(40+90*np.exp(-t*10))*t)*np.exp(-t*3)+.5*lp(nz(R,1.4),700)*np.exp(-t*7)+.3*hp(nz(R,1.4),3000)*np.exp(-t*9);return nrm(x)
    if k=='portal':
        f0=R.uniform(300,700);x=sweep(R,.5,f0,f0*R.uniform(4,7),.3,.45,3.5)+.25*tone(R.uniform(600,1200),.5,6,glide=R.uniform(1.5,2.2));return nrm(x)
    if k=='whoomp':
        t=T(.9);x=np.sin(2*np.pi*(70-30*t)*t)*np.minimum(t/.08,1)*np.exp(-t*4)+.3*sweep(R,.9,200,900,.5,.3,3);return nrm(x)
    if k=='suction':
        t=T(1.3);x=sweep(R,1.3,5000,600,.4,.95,.3)*.7+.3*np.sin(2*np.pi*np.cumsum(900-500*t/1.3)/SR)*(t/1.3);return nrm(x)
    if k=='hum':
        t=T(1.6);x=(np.sin(2*np.pi*110*t)+.5*np.sin(2*np.pi*165.5*t)+.2*np.sin(2*np.pi*331*t))*(1+.3*np.sin(2*np.pi*6*t))*np.minimum(t/.3,1)*np.minimum((1.6-t)/.2,1);return nrm(lp(x,1200))
    if k=='wub':
        t=T(.4);x=np.sin(2*np.pi*(90+60*np.sin(np.pi*t/.4))*t)*np.sin(np.pi*t/.4);return nrm(x)
    if k=='throw':return sweep(R,.6,350,4800,.35,.8,2.5)
    if k=='implode':
        t=T(1.0);suck=sweep(R,.22,5200,300,.35,.98,.2);burst=np.sin(2*np.pi*(55+200*np.exp(-t*20))*t)*np.exp(-t*4)+.5*hp(nz(R,1.0),4500)*np.exp(-t*5)
        sp=sum(tone(R.uniform(2500,6000),1.0,R.uniform(5,9))*R.uniform(.1,.25) for _ in range(6));x=np.concatenate([suck,nrm(burst+sp)]);return nrm(x)
    if k=='zap':
        t=T(.55);x=hp(nz(R,.55),2500)*(np.abs(np.sin(2*np.pi*R.uniform(40,70)*t))>.6)*np.exp(-t*7)+.5*np.sin(2*np.pi*np.cumsum(3000*np.exp(-t*8)+200)/SR)*np.exp(-t*9);return nrm(x)
    if k=='thunder':
        t=T(1.3);x=hp(nz(R,1.3),1500)*np.exp(-t*9)*.8+lp(nz(R,1.3),300)*np.exp(-t*2.5)*.9+np.sin(2*np.pi*(45+60*np.exp(-t*8))*t)*np.exp(-t*3)*.7;return nrm(x)
    if k=='airdown':return sweep(R,.8,3000,400,.5,.3,1.5)
    if k=='knock':
        t=T(.18);x=bp(nz(R,.18),600,1800)*np.exp(-t*45)+.6*np.sin(2*np.pi*R.uniform(180,240)*t)*np.exp(-t*30);return nrm(x)
    if k=='blip':return tone(R.uniform(1800,2400),.12,30,((1,1),(2,.3)))
    if k=='chirp':
        t=T(.3);x=np.sin(2*np.pi*np.cumsum(np.where((t*30).astype(int)%2==0,1600,2300)*1.0)/SR)*np.exp(-t*9);return nrm(x)
    if k=='chord':
        base=R.uniform(520,560);x=sum(tone(base*r,.9,3.5,((1,1),(2,.25))) for r in (1,1.26,1.5,2));return nrm(x)
    if k=='ratchet':
        d=.03;x=hp(nz(R,d),R.uniform(2000,4000))*np.exp(-T(d)*R.uniform(150,260))+.5*np.sin(2*np.pi*R.uniform(600,1100)*T(d))*np.exp(-T(d)*140);return nrm(x)
    if k=='clunk':
        t=T(.4);x=lp(nz(R,.4),1200)*np.exp(-t*20)+np.sin(2*np.pi*95*t)*np.exp(-t*14);return nrm(x)
    if k=='stab':
        t=T(.6);f=R.uniform(440,470);x=sum(signal.sawtooth(2*np.pi*f*r*t)*a for r,a in ((1,1),(1.5,.6),(2,.5)));return nrm(lp(x,4200)*np.exp(-t*6))
    if k=='buzz':
        t=T(.35);x=signal.square(2*np.pi*110*t)*.5+signal.square(2*np.pi*116*t)*.5;return nrm(lp(x,900)*np.exp(-t*7))
    if k=='bigwhoosh':
        t=T(1.0);x=sweep(R,1.0,200,6000,.3,.6,2.2);pan=np.linspace(-.8,.8,len(x));return np.stack([x*(1-pan)/2*1.4,x*(1+pan)/2*1.4],1)
    if k=='shimmer':return nrm(sum(tone(R.uniform(3000,7000),.8,R.uniform(4,8))*R.uniform(.2,.5) for _ in range(8)))
    if k=='revwhoosh':return sweep(R,.6,5000,300,.35,.2,2.5)
    if k=='drone':
        t=T(3.4);x=(signal.sawtooth(2*np.pi*55*t)*.5+signal.sawtooth(2*np.pi*55.6*t)*.5+.4*np.sin(2*np.pi*82.4*t));return nrm((lp(x,320)*(1-t/3.4)+lp(x,850)*(t/3.4))*np.minimum(t/1.2,1))
    if k=='lowboom':
        t=T(1.0);x=np.sin(2*np.pi*(36+40*np.exp(-t*6))*t)*np.minimum(t/.04,1)*np.exp(-t*2.6);return nrm(x)
    if k=='shing':
        t=T(.5);x=hp(nz(R,.5),5000)*np.exp(-t*8)+.5*tone(R.uniform(3500,4200),.5,6,((1,1),(1.41,.6)));return nrm(x)
    if k=='stamp':
        t=T(.6);x=np.sin(2*np.pi*(60+140*np.exp(-t*25))*t)*np.exp(-t*7)+.6*lp(nz(R,.6),1500)*np.exp(-t*25);return nrm(x)
    if k=='pad':
        t=T(1.6);x=sum(np.sin(2*np.pi*f*t+R.uniform(0,6)) for f in (261.6,329.6,392,523.3))*np.minimum(t/.9,1)*np.minimum((1.6-t)/.5,1);return nrm(lp(x,2200))
    if k=='confetti':
        t=T(1.0);x=sum(tone(R.uniform(900,4000),1.0,R.uniform(8,16))*R.uniform(.1,.3)*np.roll(np.ones(len(t)),0) for _ in range(10))+hp(nz(R,1.0),3000)*np.exp(-t*12)*.6
        pops=np.zeros(len(t))
        for _ in range(14):
            i=int(R.uniform(0,.5)*SR);L=int(.04*SR);pops[i:i+L]+=np.sin(2*np.pi*R.uniform(700,1600)*np.arange(L)/SR)*np.exp(-np.arange(L)/SR*60)
        return nrm(x+pops*.7)
    raise ValueError(k)
EV=[(0.0,'boot',-15),(0.94,'tink',-25),(3.72,'swish_up',-24),(4.10,'zoom_in',-15),(4.60,'ping',-22),(6.12,'zoom_out',-16),(6.62,'ping',-24),(7.30,'swish_dn',-27),
(8.42,'slide',-25),(9.94,'slam',-15),(10.55,'rewind',-24),(12.32,'bell',-21),(13.25,'check',-25),(13.65,'check',-25),(14.05,'check',-25),
(15.0,'riser',-24),(18.34,'boom',-9),(18.72,'swish_up',-25),(24.08,'whoomp',-16),(24.10,'ping',-25),(24.86,'suction',-19),(25.75,'hum',-25),(26.76,'wub',-21),(26.62,'throw',-19),(27.14,'implode',-9),(27.50,'ping',-27),(27.80,'swish_dn',-28),
(28.40,'zap',-12),(28.78,'thunder',-12),(29.15,'airdown',-27),(30.84,'knock',-20),(31.30,'blip',-28),(31.54,'chirp',-22),(31.96,'chord',-23),(32.85,'swish_up',-26),(33.77,'clunk',-21),(34.01,'stab',-19),
(35.02,'buzz',-25),(35.40,'bigwhoosh',-15),(36.42,'shimmer',-25),(37.6,'revwhoosh',-19),(37.8,'drone',-25),(39.2,'lowboom',-18),(41.18,'shing',-13),(41.26,'stamp',-10),(42.64,'pad',-25),(43.6,'shimmer',-27),(44.42,'confetti',-16),(44.90,'ping',-23)]
for i,f in enumerate([1400,1250,1110,990,880,780]):EV.append((9.08+i*.13,'pop',-24))
for i in range(6):EV.append((19.8+i*.32,'portal',-21))
def keys(a,b,cnt):return [(a+(b-a)*k/max(1,cnt-1),'key',-31) for k in range(cnt)]
EV+=keys(3.95,4.32,18)+keys(5.95,6.12,8)+keys(19.3,23.9,39)+keys(24.55,26.9,37)
tick_t=np.cumsum([.045*(1.18**k) for k in range(11)])+32.92
EV+=[(float(x),'ratchet',-28) for x in tick_t if x<33.75]
sfx=np.zeros((n,2),dtype=np.float32);seeds=set()
for idx,(tt,k,db) in enumerate(sorted(EV)):
    seed=1000+idx*7919;seeds.add(seed);R=np.random.default_rng(seed)
    x=S(k,R)*10**(db/20)
    if x.ndim==1:
        if k=='portal':pan=(-.6 if idx%2 else .6)
        else:pan=R.uniform(-.25,.25)
        x=np.stack([x*(1-pan)/1.0,x*(1+pan)/1.0],1)*0.75
    i0=int(tt*SR);j=min(n,i0+len(x));sfx[i0:j]+=x[:j-i0]
wr("hf/assets/audio/sfx.wav",sfx)
print("events",len(EV),"unique seeds",len(seeds))
mix=voice[:,None]+music+sfx
print("peaks voice",np.abs(voice).max(),"music",np.abs(music).max(),"sfx",np.abs(sfx).max(),"mix",np.abs(mix).max())
W=int(.5*SR);bad=0
for i in range(0,n-W,W):
    v=np.sqrt(np.mean(voice[i:i+W]**2));mu=np.sqrt(np.mean(music[i:i+W].mean(1)**2))
    if v>10**(-40/20) and mu>v*10**(-12/20):bad+=1
print("music windows within 12 dB of voice:",bad,"music rms",20*np.log10(np.sqrt(np.mean(music.mean(1)**2))),"voice",20*np.log10(vo_rms))
