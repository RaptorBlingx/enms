from hivemind_bus_client import HiveMessageBusClient
from hivemind_bus_client.identity import NodeIdentity
from ovos_bus_client import Message
import time

# --- Identity yükle ---
# Varsayılan XDG yolu: ~/.config/hivemind/_identity.json
identity = NodeIdentity()
identity.reload()
identity.site_id = "myclient"
identity.name = "myclient"

# --- HiveMessageBusClient oluştur ---
# Anahtar/parola kimliği dosyasında kayıtlı olmalı. Host/port'u burada geçiyoruz.
client = HiveMessageBusClient(identity=identity, host="10.33.10.104", port=5678)

# --- Listener’a bağlan ---
client.connect()
client.wait_for_handshake(timeout=5)
print("Connected to Hivemind listener!")

# --- Mesaj gönder ---
mycroft_msg = Message(
    "recognizer_loop:utterance",
    {"utterances": ["compare two machines"], "lang": "en-US"},
    context={
        "session": {
            "session_id": client.session_id,
            "site_id": identity.site_id
        }
    }
)
client.emit_mycroft(mycroft_msg)
print("Message sent!")

# --- Cevap bekle ---
# Örnek olarak 'speak' mesajını bekleyelim
response = client.wait_for_mycroft("speak", timeout=10.0)
print("Response:", response)

# Bağlantıyı bir süre açık tut (ör. başka mesajlar gelebilir)
time.sleep(2)
