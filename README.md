<p align="center">
  <img src="assets/vibe-commander.png" alt="Vibe Commander" width="180">
</p>

<h1 align="center">VD Speech-to-Text</h1>

<p align="center">
  <b>Konus, yapistir. Bu kadar.</b><br>
  <sub>Windows icin offline ses-yaziya donusturucu | Whisper AI</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/AI-Whisper-orange?style=flat-square&logo=openai" />
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" />
  <img src="https://img.shields.io/badge/RAM-~500MB-purple?style=flat-square" />
</p>

---

## Ne Yapar?

Mouse yan tusuna bas → konus → birak → metin aninda yapistir.

- **Tamamen offline** - internet gerektirmez
- **~500 MB RAM** - arka planda sessizce calisir
- **Turkce + Ingilizce** - sag tik ile degistir
- **Teknik terimler** - AI, GPU, GitHub gibi kelimeleri dogru tanir

## Kurulum

```
git clone https://github.com/ismail-bayraktar/vibe-commander-stt.git
cd vibe-commander-stt
setup.bat
```

`setup.bat` her seyi halleder: Python kontrolu, paket kurulumu, masaustu kisayolu.

> Ilk acilista Whisper modeli indirilir (~250 MB, bir kere).

## Kullanim

| Aksiyon | Ne Olur |
|---|---|
| **Mouse yan tus** | Kayit baslar (pill kirmizi + spektrum) |
| **Tekrar bas** | Kayit durur, metin yapistir |
| **Surukle** | Pill'i ekranda tasir |
| **Sag tik** | Ayarlar menusu |

### Sag Tik Menu

- Turkce / English gecisi
- Mikrofon secimi
- Teknik terim listesi
- Kisayol degistir (mouse/klavye)
- Windows ile otomatik baslat
- Cikis

## Ozellikler

| Ozellik | Detay |
|---|---|
| **AI Model** | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) INT8 CPU - PyTorch gerektirmez |
| **Arayuz** | Minik pill - glassmorphism dark, suruklenir |
| **Spektrum** | Kayit sirasinda canli ses dalgasi gorsellestirme |
| **Yapistir** | Transkripsiyon biter bitmez aktif pencereye Ctrl+V |
| **VAD** | Sessizlik otomatik atlanir |
| **Otostart** | Windows baslangicindan ac/kapa (sag tik menuden) |

## Yapilandirma

Ilk calistirmada `config.json` otomatik olusur:

```json
{
  "model_size": "small",
  "language": "tr",
  "hotkey": "mouse_x1",
  "beam_size": 1,
  "initial_prompt": "AI, ML, GPU, GitHub..."
}
```

| Model | RAM | Turkce Kalite |
|---|---|---|
| `tiny` | ~150 MB | Orta |
| `base` | ~250 MB | Iyi |
| **`small`** | **~500 MB** | **Cok iyi** |
| `medium` | ~1.5 GB | Mukemmel |

## Gereksinimler

- Windows 10/11
- Python 3.10+
- Mikrofon

## Katki

PR ve issue'lar memnuniyetle karsilanir.

## Lisans

[MIT](LICENSE)

---

<p align="center">
  <sub>Vibe Commander tarafindan gelistirildi</sub><br>
  <sub>Konusarak yaz, klavyeye dokunma.</sub>
</p>
