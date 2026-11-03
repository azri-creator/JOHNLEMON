# VGC Repo by Coach Am 🎬

Starter kit **Video Guna Code**. Masukkan footage atau voice-over, sebut nama style, dan Claude akan edit sampai jadi MP4 siap. Semua style dibina dengan **HyperFrames**, supaya motion lebih smooth dan padu.

---

## 1. Ambil repo ni
1. Di GitHub, tekan **Use this template → Create a new repository**.
   - Di phone, butang tu tak keluar. Buka link ni terus: **https://github.com/akramzech/VGC-Repo-by-Coach-Am/generate**
2. Bagi nama projek kau, dan pilih **Private**.
3. Buka repo baru tu dalam **Claude Code**. Ada dua cara:
   - **Laptop / Mac:** `git clone` repo tu, kemudian `cd` ke dalamnya dan taip `claude`.
   - **Phone / browser:** buka **claude.ai/code** dan pilih repo kau.

## 2. Setup (sekali sahaja)
Dalam Claude Code, taip:
```
Tolong jalankan setup.sh
```
Atau jalankan sendiri dalam Terminal:
```bash
bash setup.sh
```
Setup ni pasang Node.js, ffmpeg, package Python dan browser untuk render.

> Nak guna voice-over AI (ElevenLabs)? Kau perlu API key sendiri. Jalankan `python3 .claude/skills/elevenlabs-voiceover/scripts/voiceover.py setup` dalam Terminal. **Jangan paste key dalam chat.**

## 3. Buat video
1. Letak fail dalam folder `input/`: footage, VO, lagu, logo, gambar cut-out.
2. Beritahu Claude style yang kau nak. Contoh:
   - *"Edit footage dalam input/ guna **Native Viral**, 9:16."*
   - *"Buat motion ad guna **Konstruktivis** dari VO dalam input/vo.m4a."*
   - *"Aku ada footage bercakap, nak style yang tenang. Cadangkan 2 style."*
3. Claude akan bagi **plan dulu**. Semak, kemudian balas *"ok"*.
4. Claude bina video dan bagi **storyboard**: gambar setiap frame utama, bernombor, dengan ayat VO di bawahnya.
   - Nak ubah? Sebut nombor frame. Contoh: *"frame 3 tukar warna kuning"*, *"frame 5 tulisan besar sikit"*.
   - Claude cuma ubah frame tu dan tunjuk storyboard baru. Frame yang diubah ada bingkai kuning.
   - Bila semua dah okay, balas *"ok storyboard"*.
5. Baru Claude render video penuh. Video siap akan keluar dalam folder `output/`, bersama gambar storyboard yang kau approve.

> Kenapa storyboard dulu? Render video penuh ambil masa beberapa minit setiap kali. Storyboard siap dalam beberapa saat, jadi kau boleh betulkan semua dulu dan render sekali sahaja.

## Nak skrip dulu?
Repo ni ada **VGC Master Knowledge** dengan formula skrip Coach Am. Contoh:
- *"Tulis skrip HIKA 20 saat untuk produk aku: [fakta produk, audience, CTA]."*
- *"Pilih formula yang sesuai (HKA / HIKA / SEEIUWTOA) dan tulis satu draf."*
- *"Review video dalam output/ ikut Quality Checklist."*

Claude akan tanya maklumat yang kurang, dan takkan reka testimoni atau harga.

## Senarai style

### 🎥 Footage Sendiri
| Style | Sebut | Sesuai untuk |
|---|---|---|
| Native Viral | "Native Viral" | Reel viral, efek Claude ikut arahan |
| Astra | "Astra Style" | Explainer magenta, gaya premium gelap |
| Glow Keyword | "Glow Keyword" | Iklan TikTok/Reels, keyword bercahaya |
| PiP Explainer | "PiP Explainer" | Explainer dengan diagram, presenter dalam kotak kecil |
| Storyteller Edu | "Storyteller Edu" | Cerita tenang, kad bab, untuk pendidik |
| Journey Map Hook | "Journey Map Hook" | Iklan travel yang dibuka dengan peta 3D |
| Epic Style | "Epic Style" | Iklan travel 9:16, warna bendera ke warna brand |
| Travel Style | "Travel Style" | Travel lifestyle / pakej percutian, navy + emas |

### ✨ Motion Ad (tak perlu footage)
| Style | Sebut | Sesuai untuk |
|---|---|---|
| Clean Launch | "Clean Launch" | Launch produk, putih-biru premium |
| Konstruktivis | "Konstruktivis" | Motion paper-cut merah/hitam, tiada cut |
| Sketch Whiteboard | "Sketch Whiteboard" | Explainer lukisan tangan |
| Break Pattern | "Break Pattern" | Gambar cut-out kau + kad kertas, mustard/navy |

## Tips
- **Laptop paling stabil untuk render.** Phone sesuai untuk minta plan, skrip atau storyboard.
- Video dan audio **tidak** di-upload ke GitHub, sebab `.gitignore` dah halang. Simpan footage dalam laptop atau Dropbox kau.
- Tukar logo, warna dan CTA kepada **brand kau sendiri**. Bagi Claude logo dan brand kit kau dalam `input/`.
- Kalau render rosak, taip *"jalankan npx hyperframes doctor"*.

---
Dibina oleh **Coach Am · Video Guna Code**. Enjin video: [HyperFrames](https://github.com/heygen-com/hyperframes) (Apache-2.0). Lihat `THIRD_PARTY_NOTICES.md`.
