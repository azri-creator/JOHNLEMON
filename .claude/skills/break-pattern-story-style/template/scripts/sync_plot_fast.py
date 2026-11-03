import json, numpy as np, scipy.io.wavfile as w, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sr,v=w.read("audio/VO_Break_Pattern_EDITED.wav"); v=v.astype(np.float64)/2**31
hop=sr//100; n=len(v)//hop
env=20*np.log10(np.sqrt((v[:n*hop].reshape(n,hop)**2).mean(1))+1e-9)
tt=np.arange(n)/100
words={ # start times (energy dips + syllable timing)
 "cuba":.38,"tengok":.66,"balik":.94,"dekat":1.21,"galeri":1.49,"tu":1.9,"berapa":2.36,"banyak":2.89,"footage":3.25,"yang":3.6,"tak":3.78,"sempat":3.96,"nak":4.31,"edit":4.49,
 "nak":5.83,"potong":6.11,"video":6.55,"nak ":7.29,"letak":7.41,"subtitle":7.66,"nak  ":8.13,"cari":8.45,"b-roll":8.85,"cari ":9.46,"visual":9.85,
 "belum":11.03,"masuk":11.35,"music":11.66,"dan":11.98,"juga":12.17,"sound":12.51,"effect":12.68,"lagi":13.02,
 "sedar":14.24,"dah":15.0,"3":15.19,"jam":15.57,"depan":15.76,"laptop":16.14,
 "video ":17.39,"tak ":17.81,"siap":17.95,"nak   ":18.47,"post":18.82,"pun":19.07,"dah ":19.17,"tak  ":19.31,"larat":19.49,
 "dalam":21.06,"panduan":21.46,"video  ":21.93,"guna":22.33,"kod":22.75,
 "VGC":23.65,"korang":25.07,"akan":25.35,"belajar":25.63,"macam":26.97,"mana":27.27,"nak    ":27.57,"automate":27.86,"editing":28.38,
 "guna ":29.52,"chatGPT":29.96,"ataupun":30.67,"claude":31.11,
 "campak":32.53,"footage ":32.84,"tidur":33.73,"dah siap":34.33,
 "daripada":36.09,"rakaman":36.79,"yang ":37.27,"raw":37.43,"macam ":37.59,"ni":37.91,"terus":38.94,"jadi":39.35,"video   ":39.65,"macam  ":40.15,"ni ":40.43,
 "ada":47.31,"tutorial":47.65,"ada ":48.45,"template":48.89,"ada  ":49.37,"group":49.62,"support":49.99,
 "belajar ":51.21,"dari":51.77,"basic":52.14,"sampai":52.63,"advance":53.17,"jadi ":53.89,"expert":54.25,
 "nak     ":55.86,"mula":56.02,"posting":56.34,"hari":56.66,"hari ":56.98,
 "klik":58.17,"link":58.4,"daftar":58.89,"sekarang":59.2}
hits=[1.22,2.36,2.66,3.05,3.3,3.78,4.42,6.05,7.3,8.4,9.46,11.3,12.3,14.24,15.28,15.57,16.12,17.36,18.8,19.5,21.46,21.93,22.33,22.75,23.65,25.5,26.95,27.86,28.38,29.95,31.1,31.5,31.78,32.53,32.86,33.74,34.62,36.09,36.79,38.94,39.35,39.65,47.2,47.45,48.62,49.55,51.2,52.14,53.17,54.28,55.86,56.02,56.66,58.1,58.89,59.2]
RM=json.load(open("audio/retime_map.json"))
TM=lambda t: float(np.interp(t,RM["xs"],RM["ys"]))
words={k:TM(t) for k,t in words.items()}; hits=[TM(t) for t in hits]
fig,axs=plt.subplots(4,1,figsize=(26,14))
for i,ax in enumerate(axs):
    a,b=i*12.2,(i+1)*12.2
    m=(tt>=a)&(tt<b)
    ax.plot(tt[m],env[m],lw=0.9,color="#222"); ax.set_ylim(-60,0); ax.set_xlim(a,b)
    for k,t in words.items():
        if a<=t<b: ax.axvline(t,color="#1b7",lw=0.8,alpha=.6); ax.text(t,-4-((hash(k)%5)*3),k.strip(),rotation=0,fontsize=9,color="#064",va="top")
    for t in hits:
        if a<=t<b: ax.axvline(t,color="r",lw=1.6,alpha=.75); ax.text(t,-57,f"{t:.2f}",fontsize=8,color="r",rotation=90,va="bottom")
plt.tight_layout(); plt.savefig("qc/sync_fast.png",dpi=60)
