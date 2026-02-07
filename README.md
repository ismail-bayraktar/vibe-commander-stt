# VD Speech-to-Text

> Windows icin hafif, hizli, offline ses-yaziya donusturucu. Whisper AI ile Turkce ve Ingilizce destek.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Whisper](https://img.shields.io/badge/AI-Whisper-orange?logo=openai)](https://github.com/openai/whisper)
[![Windows](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows)](https://www.microsoft.com/windows)

---

## Ne Yapar?

Konusursun, yazdigi yere yapistir. Bu kadar.

- **Yan tusa bas** → kayit baslar (pill kirmizi olur)
- **Tekrar bas** → kayit durur, metin aninda yapistir (Ctrl+V)
- **Tamamen offline** - internet gerektirmez
- **~500 MB RAM** - arka planda sessizce calisir

## Ozellikler

| Ozellik | Detay |
|---|---|
| **AI Model** | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (INT8 CPU) - PyTorch gerektirmez |
| **Diller** | Turkce, Ingilizce (sag tik ile degistir) |
| **Tetikleyici** | Mouse yan tus, orta tik, veya klavye kisayolu |
| **Arayuz** | Suruklenen minik pill - glassmorphism dark tema |
| **Spektrum** | Kayit sirasinda canli ses dalgasi gorsellestirme |
| **Terimler** | AI, ML, GPU gibi teknik terimleri dogru tanir |
| **Otostart** | Windows ile otomatik baslat (sag tik menuden) |
| **Yapistir** | Transkripsiyon aninda aktif pencereye Ctrl+V yapar |

## Kurulum

### Hizli (setup.bat)

```
git clone https://github.com/user/vd-speech-to-text.git
cd vd-speech-to-text
setup.bat
```

`setup.bat` her seyi halleder: Python kontrolu, paket kurulumu, masaustu kisayolu.

### Manuel

```bash
pip install -r requirements.txt
python speech_to_text.py
```

**Gereksinimler:** Python 3.10+, Windows 10/11

## Kullanim

1. **Baslat**: Masaustu kisayolu veya `python speech_to_text.py`
2. **Kayit**: Mouse yan tusa bas (veya ayarladigin kisayol)
3. **Durdur**: Ayni tusa tekrar bas
4. **Sonuc**: Metin otomatik yapistir

### Sag Tik Menu

- Turkce / English gecisi
- Mikrofon secimi
- Teknik terim listesi
- Kisayol degistir
- Windows ile baslat toggle
- Cikis

## Yapilandirma

Ilk calistirmada `config.json` otomatik olusur:

```json
{
  "model_size": "small",
  "language": "tr",
  "hotkey": "mouse_x1",
  "beam_size": 1,
  "initial_prompt": "GTRL, RL, AI, ML, DQN, PPO..."
}
```

| Ayar | Aciklama | Varsayilan |
|---|---|---|
| `model_size` | Whisper model boyutu (`tiny`, `base`, `small`, `medium`) | `small` |
| `language` | Transkripsiyon dili | `tr` |
| `hotkey` | Tetikleyici (`mouse_x1`, `mouse_middle`, `ctrl+shift+space`...) | `mouse_x1` |
| `initial_prompt` | Teknik terimler (Whisper'a ipucu verir) | AI/ML terimleri |
| `beam_size` | Whisper beam size (1=hizli, 5=kaliteli) | `1` |

## Model Boyutlari

| Model | RAM | Hiz | Turkce Kalite |
|---|---|---|---|
| `tiny` | ~150 MB | Cok hizli | Orta |
| `base` | ~250 MB | Hizli | Iyi |
| **`small`** | **~500 MB** | **Normal** | **Cok iyi** |
| `medium` | ~1.5 GB | Yavas | Mukemmel |

> `small` cogu kullanim icin en iyi denge.

## Teknik Detaylar

- **Ses yakalama**: `sounddevice` (PortAudio) - 16kHz mono float32
- **Transkripsiyon**: `faster-whisper` - CTranslate2 INT8 CPU, VAD filtresi
- **GUI**: `tkinter` + `Pillow` - anti-aliased pill, 4x supersampled
- **Hotkey**: `keyboard` + `pynput` - mouse/klavye destegi
- **Yapistirma**: `pynput` Ctrl+V simulasyonu
- **Thread modeli**: Ana (GUI) + Hotkey + Ses + Transkripsiyon

## SSS

**S: Bluetooth kulaklik mikrofonu kullanabilir miyim?**
Teknik olarak evet, ama Windows BT mikrofon acildiginda ses profilini SCO'ya dusurur ve muzik kalitesi bozulur. Dahili mikrofon (Realtek) onerilir.

**S: Maksimum kayit suresi?**
Teknik limit yok. Pratik olarak 2-3 dakika ideal. Cok uzun kayitlarda RAM artar.

**S: Neden bazen yanlis yapistirir?**
Ctrl+V simulasyonu o an aktif olan pencereye gider. Kayit dururken imlecin dogru yerde oldugundan emin olun.

## Katki

PR'lar ve issue'lar memnuniyetle karsilanir! Turkce veya Ingilizce yazabilirsiniz.

## Lisans

[MIT](LICENSE) - istediginiz gibi kullanin.

---

<p align="center">
  <b>VD Speech-to-Text</b> - Konusarak yaz, klavyeye dokunma.<br>
  <sub>Vibe Commander tarafindan gelistirildi</sub>
</p>
