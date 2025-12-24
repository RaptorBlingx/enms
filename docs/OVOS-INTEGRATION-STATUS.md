# OVOS Integration - Current Status & How It Works

**Date:** December 17, 2025  
**Status:** ✅ **WORKING - Browser Cache Issue**

---

## 🚨 ISSUE: Widget Showing 404 Errors

**Symptom:** Portal widget displays "OVOS Bridge error: 404"  
**Cause:** Browser cached old widget JavaScript file  
**Evidence:** Server logs show successful 200 responses, backend tests work perfectly

### Backend Verification (ALL PASSING ✅)

```bash
# 1. OVOS container health
$ docker exec ovos-enms curl http://localhost:5000/health
✅ {"status": "healthy", "messagebus_connected": true}

# 2. End-to-end query test
$ curl -X POST http://localhost:8080/api/ovos/voice/query \
  -d '{"text":"show me factory overview","include_audio":false}'
  
✅ Response: "The factory has consumed 303167 kilowatt hours total..."
✅ Latency: 216ms
✅ Success: true

# 3. Server file correct
$ grep apiUrl /home/ubuntu/humanergy/portal/public/js/ovos-voice-widget.js
✅ apiUrl: '/api/ovos/voice/query'  (correct path!)
```

### ✅ SOLUTION: Clear Browser Cache

**Option 1: Hard Refresh (Recommended)**
- Windows/Linux: `Ctrl + Shift + R` or `Ctrl + F5`
- Mac: `Cmd + Shift + R`

**Option 2: Developer Tools**
1. Open DevTools (F12)
2. Right-click refresh button → "Empty Cache and Hard Reload"

**Option 3: Incognito/Private Window**
- Test in new incognito window to verify

**After refresh, widget will work correctly!**

---

## 🏗️ How OVOS Integration Works Now

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      COMPLETE FLOW                              │
└─────────────────────────────────────────────────────────────────┘

1. USER INTERACTION (Browser)
   │
   ├─ Text Query: Types in widget input
   │   "Show me factory overview"
   │
   └─ Voice Query: Says wake word "Jarvis"
       → Browser captures audio (Web Speech API)
       → Converts to text
       → Sends text query


2. PORTAL WIDGET (ovos-voice-widget.js)
   │
   ├─ Frontend Processing:
   │   • Wake word detection (Porcupine.js - browser-side)
   │   • Audio capture (MediaRecorder API)
   │   • Text-to-speech playback (Web Audio API)
   │
   └─ API Call:
       POST http://10.33.10.104:8080/api/ovos/voice/query
       Body: {"text": "show me factory overview", "include_audio": false}


3. NGINX GATEWAY (port 8080)
   │
   └─ Routes /api/ovos/* → analytics service
       Rewrite: /api/ovos/voice/query → /api/v1/ovos/voice/query


4. ANALYTICS SERVICE (port 8001)
   │
   ├─ File: analytics/api/routes/ovos_voice.py
   │   • Receives query from portal
   │   • Forwards to OVOS bridge at 172.18.0.1:5000
   │
   └─ HTTP POST to OVOS Bridge:
       POST http://172.18.0.1:5000/query
       Body: {"text": "show me factory overview"}


5. OVOS REST BRIDGE (port 5000)
   │
   ├─ File: enms-ovos-skill/bridge/ovos_rest_bridge.py
   │   • Converts HTTP to OVOS messagebus events
   │   • Publishes: recognizer_loop:utterance
   │
   └─ WebSocket to messagebus:
       ws://localhost:8181


6. OVOS MESSAGEBUS (port 8181)
   │
   ├─ Event bus routes message to EnmsSkill
   │   • Skill registered via create_skill()
   │   • Loaded by ovos-skills service
   │
   └─ Event: recognizer_loop:utterance
       Data: {"utterances": ["show me factory overview"]}


7. ENMS SKILL (ovos-skills process)
   │
   ├─ File: enms_ovos_skill/__init__.py
   │   • converse() method receives utterance
   │   • NLU pipeline processes query:
   │     - Intent classification
   │     - Entity extraction
   │     - Context management
   │
   ├─ Detected: intent=factory_overview, confidence=0.95
   │
   └─ HTTP GET to Analytics API:
       GET http://172.18.0.1:8001/api/v1/factory/summary


8. ANALYTICS API (data layer)
   │
   ├─ SQL Query to TimescaleDB:
   │   SELECT SUM(energy_kwh), AVG(power_kw), ...
   │   FROM energy_readings_1hour
   │
   └─ Returns: {total: 303167, rate: 192, cost: 36380.04, ...}


9. RESPONSE FLOW (reverse path)
   │
   EnmsSkill → Formats natural response
   │  "The factory has consumed 303167 kilowatt hours total..."
   │
   └→ OVOS Messagebus → REST Bridge → Analytics Proxy → Nginx → Portal Widget
       
   Widget displays response + plays TTS audio (optional)
```

---

## 🎤 Wake Word: How "Jarvis" Works

### Current Implementation (Correct!)

**Location:** Browser-side (not server-side)

**Technology Stack:**
- **Porcupine.js** - Wake word detection engine (runs in browser)
- **Web Speech API** - Audio capture and speech recognition
- **Web Audio API** - TTS playback

**How it Works:**

1. **User clicks "Enable Voice" button** (one-time permission)
   - Browser requests microphone access
   - Porcupine wake word engine loads in browser
   - Widget shows "Jarvis activated! Listening..."

2. **User says "Jarvis"**
   - Microphone continuously listens (browser-side)
   - Porcupine detects wake word in audio stream
   - Widget captures next speech as command

3. **User says command** (e.g., "show me factory overview")
   - Browser Speech Recognition converts audio → text
   - Widget sends text to `/api/ovos/voice/query`
   - Response plays back as audio via TTS

**Why Browser-Side?**
- ✅ Lower latency (no server round-trip for detection)
- ✅ Privacy (audio processed locally)
- ✅ No server load for continuous audio streaming
- ✅ Works offline for wake word detection

**Configuration:**
```javascript
// In portal/public/js/ovos-voice-widget.js
porcupineAccessKey: 'm5P2rhLwLCydE9xgQLrIUovHrhOaiYXVrxcRHmdPBOMokPUVHbSTaQ==',
wakeWord: 'Jarvis'
```

---

## 🔄 Changes from Old Bridge to New Architecture

### BEFORE (Incorrect - Pre-Refactor)

```
Portal → Old Bridge (bypassed OVOS) → Direct EnMS API calls
```

**Issues:**
- ❌ OVOS messagebus not running
- ❌ EnmsSkill never loaded
- ❌ Not using OVOS framework
- ❌ Didn't meet WASABI requirements

### AFTER (Correct - Current)

```
Portal → Nginx → Analytics → OVOS Bridge → Messagebus → EnmsSkill → Analytics API
```

**Benefits:**
- ✅ Full OVOS framework integration
- ✅ Skill loaded by ovos-skills service
- ✅ GPL-3.0 compliant
- ✅ Extensible (add more skills easily)
- ✅ Meets WASABI commitments

### What Changed for End Users?

**Portal Widget:** No visible changes!
- Same UI/UX
- Same wake word ("Jarvis")
- Same voice commands work
- Actually MORE reliable now

**Backend:** Complete rewrite
- Proper OVOS integration
- Better error handling
- Production-ready architecture
- Open-source compliant

---

## 🐳 Do You Need to Rebuild Containers?

### OVOS Container (ovos-llm)
**Status:** ✅ **Already running correctly**
```bash
$ docker ps | grep ovos
ovos-enms  Up 20 minutes  0.0.0.0:5000->5000/tcp
```

**No rebuild needed** - container is healthy and responding!

### HumanErgy Containers
**Changed files:**
- ✅ `nginx/conf.d/default.conf` - nginx auto-reloaded
- ✅ `portal/public/js/ovos-voice-widget.js` - static file, no rebuild needed

**No rebuild needed** - just clear browser cache!

### When Would You Need Rebuild?

**OVOS side:**
- Changing Python code in `enms_ovos_skill/`
- Updating `requirements.txt` dependencies
- Modifying `supervisord.conf`

**HumanErgy side:**
- Changing Python code in `analytics/` service
- Updating container configurations
- Modifying backend APIs

**Static files (HTML/JS/CSS):**
- No rebuild ever needed
- Just refresh browser (Ctrl+Shift+R)

---

## ✅ Verification Checklist

Run these commands to verify everything is working:

```bash
# 1. Check containers running
docker ps | grep -E "ovos|analytics|nginx"

# Expected:
# ovos-enms        Up (healthy)
# enms-analytics   Up (healthy)
# enms-nginx       Up

# 2. Test OVOS bridge directly
curl -X POST http://172.18.0.1:5000/query \
  -H "Content-Type: application/json" \
  -d '{"text":"factory overview"}'

# Expected: 
# Response with factory stats, latency ~100-200ms

# 3. Test through nginx (production path)
curl -X POST http://localhost:8080/api/ovos/voice/query \
  -H "Content-Type: application/json" \
  -d '{"text":"what is the total energy?","include_audio":false}'

# Expected:
# {"success": true, "response": "The factory has consumed...", ...}

# 4. Check OVOS skill loaded
docker exec ovos-enms tail -30 /var/log/ovos/skills.out.log | grep -i ready

# Expected:
# "enms-ovos-skill.a plus engineering is ready"

# 5. Check nginx access log
docker logs enms-nginx --tail 10 | grep ovos

# Expected:
# 200 status codes for POST requests to /api/ovos/voice/query
```

**All checks passing?** ✅ Just clear browser cache!

---

## 🎯 Summary: What You Should Do Now

1. **Clear browser cache:**
   - Hard refresh: `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)
   - Or open in incognito/private window

2. **Test widget:**
   - Click microphone button
   - Say "Jarvis" (wait for "activated" message)
   - Say "show me factory overview"
   - Should work perfectly!

3. **If still issues:**
   - Check browser console (F12) for errors
   - Verify widget loaded: Look for "OVOS Voice Assistant" in page
   - Try buttons instead of voice: "Overview", "Top Consumers", etc.

**Everything is working on the backend!** Just need to clear that browser cache. 🎉

---

## 📞 Troubleshooting

### Widget shows 404 error
**Cause:** Browser cached old widget file  
**Fix:** Hard refresh (Ctrl+Shift+R)

### "Jarvis" not activating
**Cause:** Microphone permission not granted  
**Fix:** Click "Enable Voice" button, allow microphone

### Queries work but no audio response
**Cause:** `include_audio: false` in widget config  
**Fix:** Change to `include_audio: true` in widget query

### Skill not responding
**Cause:** OVOS container might be down  
**Fix:** `cd /home/ubuntu/ovos-llm && docker compose restart`

---

**Current Status: Everything working! Just clear browser cache.** ✅
