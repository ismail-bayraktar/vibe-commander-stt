<p align="center">
  <img src="assets/vibe-commander.png" alt="Vibe Commander" width="180">
</p>

<h1 align="center">VD Speech-to-Text</h1>

<p align="center">
  <b>Konus, yapistir. Bu kadar.</b><br>
  <sub>Windows icin offline ses-yaziya donusturucu | Whisper AI | GPU destekli</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/AI-Whisper_large--v3-orange?style=flat-square&logo=openai" />
  <img src="https://img.shields.io/badge/GPU-CUDA_float16-76B900?style=flat-square&logo=nvidia" />
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" />
</p>

---

## Ne Yapar?

Mouse yan tusuna bas &rarr; konus &rarr; birak &rarr; metin aninda yapistir.

- **GPU hizlandirmali** - NVIDIA GPU ile large-v3 modeli, ~1 saniyede transkripsiyon
- **Tamamen offline** - internet gerektirmez (model bir kere indirilir)
- **Lazy load** - Windows ile baslar ama modeli ilk kullanima kadar yuklemez, sistemi yormaz
- **Akilli yapistirma** - aktif pencereyi otomatik algilar, terminallere Shift+Insert, GUI'ye Ctrl+V
- **Turkce + Ingilizce** - sag tik ile degistir
- **Teknik terimler** - AI, GPU, GitHub, transformer gibi kelimeleri dogru tanir

## Kurulum

```
git clone https://github.com/ismail-bayraktar/vibe-commander-stt.git
cd vibe-commander-stt
setup.bat
```

`setup.bat` her seyi halleder: Python kontrolu, paket kurulumu, masaustu kisayolu.

> Ilk kullanmimda Whisper modeli indirilir (~1.5 GB large-v3, bir kere).

### GPU Destegi (Opsiyonel, Onerilen)

NVIDIA GPU varsa (RTX serisi vb.) buyuk fark yaratir:

```
pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
```

| | CPU (small, int8) | GPU (large-v3, float16) |
|---|---|---|
| **Hiz** | 3-8 sn | 0.5-2 sn |
| **Kalite** | Iyi | Cok iyi |
| **RAM/VRAM** | ~500 MB RAM | ~1.5 GB VRAM |

GPU yoksa otomatik olarak CPU modunda calisir.

## Kullanim

| Aksiyon | Ne Olur |
|---|---|
| **Mouse yan tus** | Kayit baslar (pill kirmizi + spektrum) |
| **Tekrar bas** | Kayit durur, metin yapistir |
| **Surukle** | Pill'i ekranda tasi |
| **Sag tik pill** | Ayarlar menusu |
| **Sag tik tray** | Ayarlar menusu (sistem tepsisinden) |

### Sag Tik Menu

- Turkce / English gecisi
- Mikrofon secimi
- Teknik terim listesi (terimler duzenlenebilir)
- Kisayol degistir (mouse/klavye)
- Yapistirma modu (Otomatik / Ctrl+V / Shift+Insert)
- Windows ile otomatik baslat
- Cikis

### Calistirma Modlari

| Yontem | Terminal | Kullanim |
|---|---|---|
| `pythonw start_vd.pyw` | Yok | Gunluk kullanim |
| `python speech_to_text.py` | Loglar gorunur | Debug |
| Masaustu kisayolu | Yok | En kolay |

## Mimari

```
Baslangic (Windows boot)          Ilk kullanim
       |                                |
  Pill + Tray gorunur              Tusa bas
  Model YUKLENMEZ                      |
  RAM: ~30 MB                    Model yuklenir (5-10 sn)
       |                              |
  Idle bekler...              Kayit baslar otomatik
                                       |
                              Transkripsiyon (~1 sn GPU)
                                       |
                              Aktif pencereye yapistir
```

## Ozellikler

| Ozellik | Detay |
|---|---|
| **AI Model** | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) - GPU: large-v3 float16, CPU: small int8 |
| **Arayuz** | Glassmorphism pill (72x28px) + sistem tepsisi ikonu |
| **Spektrum** | Kayit sirasinda canli ses dalgasi gorsellestirme |
| **Yapistirma** | Akilli pencere algilama - terminal/GUI otomatik ayirt eder |
| **Ses isleme** | Peak normalizasyon + VAD filtresi + hallusinasyon filtresi |
| **Lazy load** | Model ilk kullanima kadar yuklenmez, Windows bootu etkilenmez |
| **Otostart** | Windows baslangicina ekle/cikar (sag tik menuden) |
| **Turkce optimizasyon** | initial_prompt ile dogru noktalama ve karakter kullanimi |

## Yapilandirma

Ilk calistirmada `config.json` otomatik olusur:

```json
{
  "model_size": "small",
  "gpu_model_size": "large-v3",
  "language": "tr",
  "hotkey": "mouse_x1",
  "beam_size": 1,
  "paste_method": "auto",
  "initial_prompt": "Merhaba, bu bir Turkce konusma kaydidir. AI, ML, GPU..."
}
```

| Ayar | Aciklama |
|---|---|
| `model_size` | CPU modeli (tiny/base/small/medium) |
| `gpu_model_size` | GPU modeli (large-v3 onerilen) |
| `paste_method` | auto / ctrl_v / shift_insert |
| `initial_prompt` | Teknik terimler ve dil ipucu |

### Model Secimi

`config.json` dosyasindaki `model_size` (CPU) ve `gpu_model_size` (GPU) degerlerini degistirerek farkli modeller kullanabilirsiniz. Daha kucuk model = daha az kaynak tuketimi, daha buyuk model = daha iyi kalite.

**GPU modelleri** (`gpu_model_size`):

| Model | VRAM | Hiz | Turkce Kalite | Kime Uygun |
|---|---|---|---|---|
| `tiny` | ~1 GB | Aninda | Dusuk | Hizli not alma, kisa cumleler |
| `base` | ~1 GB | Cok hizli | Orta | Gunluk kullanim, hafif GPU |
| `small` | ~1.5 GB | Hizli | Iyi | Dengeli secim |
| `medium` | ~2.5 GB | Orta | Cok iyi | Kalite oncelikliyse |
| **`large-v3`** | **~3 GB** | **Hizli** | **En iyi** | **Onerilen (RTX 3060+)** |

**CPU modelleri** (`model_size`):

| Model | RAM | Hiz | Turkce Kalite | Kime Uygun |
|---|---|---|---|---|
| `tiny` | ~150 MB | Hizli | Dusuk | Eski/zayif bilgisayar |
| `base` | ~250 MB | Orta | Orta | 4 GB RAM sistemi |
| **`small`** | **~500 MB** | **Orta** | **Iyi** | **Onerilen (GPU yoksa)** |
| `medium` | ~1.5 GB | Yavas | Cok iyi | 8 GB+ RAM, sabir varsa |

**Ornek**: Dusuk VRAM'li bir GPU icin `config.json`'da:
```json
{
  "gpu_model_size": "small",
  "model_size": "tiny"
}
```

> Model degisikligi sonrasi uygulamayi yeniden baslatin. Yeni model ilk kullanmimda otomatik indirilir.

## Gereksinimler

- Windows 10/11
- Python 3.10+
- Mikrofon
- NVIDIA GPU (opsiyonel, onerilen)

## Katki

PR ve issue'lar memnuniyetle karsilanir.

## Lisans

[MIT](LICENSE)

---

<p align="center">
  <sub>Vibe Commander tarafindan gelistirildi</sub><br>
  <sub>Konusarak yaz, klavyeye dokunma.</sub>
</p>
