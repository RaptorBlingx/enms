# 🚀 Sistem Nasıl Başlatılır?

Artık sistem **tek komutla** çalışıyor! Backend (Rasa) ve Frontend otomatik olarak birlikte başlatılır.

## ⚡ Hızlı Başlangıç

### 1. Bağımlılıkları Yükle
```bash
cd /home/burak/Desktop/chatbot
npm install
```

### 2. Rasa Model Dosyasını Çıkar (İlk Kez)
```bash
cd models
tar -xzf 20251126-090737-matte-nailer.tar.gz
cd ..
```

### 3. Sistemi Başlat
```bash
npm run dev
```

Bu komut:
- ✅ Backend server'ı başlatır (port 5006)
- ✅ Rasa'yı otomatik başlatır (port 5005)
- ✅ Frontend'i başlatır (port 3000)

## 📋 Detaylı Adımlar

### Gereksinimler
- ✅ Node.js (v18+)
- ✅ Python 3.8+
- ✅ Rasa (`pip install rasa`)

### Rasa Kurulumu (Eğer yoksa)
```bash
# Python ve pip kontrolü
python3 --version
pip3 --version

# Rasa'yı kur
pip3 install rasa

# Kurulumu doğrula
rasa --version
```

### Model Dosyasını Çıkarma
Model dosyası sadece ilk kez çıkarılması gerekir:
```bash
cd /home/burak/Desktop/chatbot/models
tar -xzf 20251126-090737-matte-nailer.tar.gz
```

### Sistemi Çalıştırma

**Tek komutla (Önerilen):**
```bash
npm run dev
```

**Ayrı ayrı çalıştırmak isterseniz:**
```bash
# Terminal 1: Backend
npm run dev:backend

# Terminal 2: Frontend
npm run dev:frontend
```

## 🌐 Erişim

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5006
- **Rasa Server**: http://localhost:5005 (otomatik başlatılır)

## 🔍 Kontrol

Backend'in çalışıp çalışmadığını kontrol etmek için:
```bash
curl http://localhost:5006/health
```

## ❌ Sorun Giderme

### "Rasa bulunamadı" hatası
```bash
# Rasa kurulu mu kontrol et
rasa --version

# Yoksa kur
pip3 install rasa
```

### "Model klasörü bulunamadı" hatası
```bash
cd models
tar -xzf 20251126-090737-matte-nailer.tar.gz
```

### Port zaten kullanımda
- Port 3000, 5005 veya 5006 kullanımda olabilir
- Kullanan process'i bulun: `lsof -i :3000` veya `netstat -tlnp | grep 3000`
- Process'i durdurun veya port'u değiştirin

### Backend başlamıyor
- Node.js sürümünü kontrol edin: `node --version` (v18+ olmalı)
- Bağımlılıkları yeniden yükleyin: `npm install`

## 📝 Notlar

- İlk başlatmada Rasa'nın yüklenmesi birkaç saniye sürebilir
- Backend otomatik olarak Rasa'yı başlatır ve yönetir
- Ctrl+C ile tüm servisler birlikte durdurulur
- Model dosyası sadece bir kez çıkarılması gerekir

