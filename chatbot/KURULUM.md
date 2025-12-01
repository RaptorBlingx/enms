# Sistem Kurulum ve Çalıştırma Rehberi

## 1. Node.js ve npm Kurulumu

Sistemi çalıştırmak için önce Node.js ve npm'in kurulu olması gerekiyor.

### Ubuntu/Debian için:
```bash
# Node.js ve npm'i kur
sudo apt update
sudo apt install nodejs npm

# Kurulumu doğrula
node --version
npm --version
```

### Alternatif: nvm ile kurulum (önerilen)
```bash
# nvm'i kur
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Terminal'i yeniden başlat veya:
source ~/.bashrc

# Node.js'in en son LTS sürümünü kur
nvm install --lts
nvm use --lts
```

## 2. Proje Bağımlılıklarını Yükle

```bash
cd /home/burak/Desktop/chatbot
npm install
```

## 3. Gemini API Anahtarı Ayarla

1. Google AI Studio'dan API anahtarınızı alın: https://aistudio.google.com/apikey
2. `.env.local` dosyası oluşturun:
```bash
echo "GEMINI_API_KEY=buraya_api_anahtarinizi_yazin" > .env.local
```

Veya manuel olarak `.env.local` dosyası oluşturup içine şunu yazın:
```
GEMINI_API_KEY=buraya_api_anahtarinizi_yazin
```

## 4. Sistemi Çalıştır

```bash
npm run dev
```

Sistem `http://localhost:3000` adresinde çalışacaktır.

## Hızlı Başlangıç (Tüm Adımlar)

```bash
# 1. Node.js kur (eğer yoksa)
sudo apt update && sudo apt install nodejs npm

# 2. Bağımlılıkları yükle
cd /home/burak/Desktop/chatbot
npm install

# 3. API anahtarını ayarla (.env.local dosyası oluştur)
echo "GEMINI_API_KEY=buraya_api_anahtarinizi_yazin" > .env.local

# 4. Çalıştır
npm run dev
```

## Sorun Giderme

- **npm komutu bulunamıyor**: Node.js ve npm'i kurun (yukarıdaki adım 1)
- **API hatası**: `.env.local` dosyasında `GEMINI_API_KEY` değerinin doğru olduğundan emin olun
- **Port 3000 kullanımda**: `vite.config.ts` dosyasında port numarasını değiştirebilirsiniz

