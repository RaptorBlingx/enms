# Rasa Server Kurulum ve Çalıştırma Rehberi

Bu proje artık Rasa chatbot modelini kullanmaktadır. Rasa'yı çalıştırmak için aşağıdaki adımları takip edin.

## 1. Python ve Rasa Kurulumu

### Python Kurulumu (3.8 veya üzeri)
```bash
# Python sürümünü kontrol et
python3 --version

# Eğer yoksa kur
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Rasa Kurulumu
```bash
# Rasa'yı kur
pip3 install rasa

# Veya virtual environment kullanarak (önerilen)
python3 -m venv rasa_env
source rasa_env/bin/activate
pip install rasa
```

## 2. Rasa Model Dosyasını Çıkarma

Models klasöründeki model dosyanızı çıkarın:

```bash
cd /home/burak/Desktop/chatbot/models
tar -xzf 20251126-090737-matte-nailer.tar.gz
```

Bu işlem bir klasör oluşturacak (örneğin: `20251126-090737-matte-nailer`).

## 3. Rasa Server'ı Başlatma

### Seçenek 1: Model klasöründen direkt çalıştırma
```bash
cd /home/burak/Desktop/chatbot/models/20251126-090737-matte-nailer
rasa run --enable-api --cors "*" --port 5005
```

### Seçenek 2: Model dosyasını başka bir yere kopyalayıp çalıştırma
```bash
# Model klasörünü kopyala
cp -r /home/burak/Desktop/chatbot/models/20251126-090737-matte-nailer ~/rasa_model

# Rasa server'ı başlat
cd ~/rasa_model
rasa run --enable-api --cors "*" --port 5005
```

## 4. Frontend'i Çalıştırma

Yeni bir terminal penceresi açın ve:

```bash
cd /home/burak/Desktop/chatbot

# Rasa server URL'ini ayarla (opsiyonel, varsayılan localhost:5005)
echo "VITE_RASA_SERVER_URL=http://localhost:5005" > .env.local

# Frontend'i başlat
npm run dev
```

## 5. Test Etme

1. Rasa server'ın çalıştığını kontrol edin:
   ```bash
   curl http://localhost:5005/webhooks/rest/webhook -X POST \
     -H "Content-Type: application/json" \
     -d '{"sender": "test", "message": "Merhaba"}'
   ```

2. Tarayıcıda `http://localhost:3000` adresini açın ve chatbotu test edin.

## Önemli Notlar

- **Rasa server** ve **frontend** aynı anda çalışmalıdır
- Rasa server varsayılan olarak `http://localhost:5005` portunda çalışır
- Eğer farklı bir port kullanmak isterseniz, `.env.local` dosyasında `VITE_RASA_SERVER_URL` değişkenini ayarlayın
- CORS ayarları Rasa server'da `--cors "*"` parametresi ile aktif edilmiştir

## Sorun Giderme

### Rasa server başlamıyor
- Python ve Rasa'nın doğru kurulduğundan emin olun
- Model dosyasının doğru çıkarıldığından emin olun
- Port 5005'in kullanımda olmadığından emin olun

### Frontend Rasa'ya bağlanamıyor
- Rasa server'ın çalıştığından emin olun
- `.env.local` dosyasında `VITE_RASA_SERVER_URL` değerini kontrol edin
- Tarayıcı konsolunda hata mesajlarını kontrol edin

### CORS hatası
- Rasa server'ı `--cors "*"` parametresi ile başlattığınızdan emin olun

## Hızlı Başlangıç (Tüm Adımlar)

```bash
# 1. Rasa'yı kur (eğer yoksa)
pip3 install rasa

# 2. Model dosyasını çıkar
cd /home/burak/Desktop/chatbot/models
tar -xzf 20251126-090737-matte-nailer.tar.gz

# 3. Rasa server'ı başlat (Terminal 1)
cd 20251126-090737-matte-nailer
rasa run --enable-api --cors "*" --port 5005

# 4. Frontend'i başlat (Terminal 2)
cd /home/burak/Desktop/chatbot
npm run dev
```

