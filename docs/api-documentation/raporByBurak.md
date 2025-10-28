## 1. Introduction {#introduction}

This report presents the description, deployment results, validation,
and testing feedback of the **OVOS Energy Visualization Skill**,
developed to enhance energy monitoring and analytics capabilities in the
OVOS ecosystem. The skill connects to Energy Management System (EMS)
REST/WS APIs to retrieve machine-level energy data and provides
interactive, voice-driven summaries with optional TTS feedback.

## 2. Skill Overview {#skill-overview}

**OVOS Energy Visualization Skill** enables:

- Voice-controlled retrieval of energy consumption and machine data.
- Real-time summaries of machine energy use.
- Visualization outputs including daily and hourly heatmaps and Sankey
  diagrams.
- Optional voice-based TTS feedback for hands-free operation.
- Publishing results on the OVOS message bus under *api.response*.

### 2.1 Features {#features}

- **Machine List**: Active/inactive summary of all machines.
- **Energy Consumption**: Last 24-hour summaries for individual
  machines.
- **Heatmaps**: Daily and hourly energy heatmaps.
- **Anomalies**: Detection and summary of abnormal energy consumption
  events.
- **TTS Feedback**: Optional voice output of energy data and analytics.

## 3. Deployment & Installation {#deployment-installation}

1.  Include the skill repository in the OVOS container image or copy it
    to the existing OVOS installation.
2.  Python dependencies are defined in *setup.py* and installed
    automatically in Docker.
3.  Language and resource directories use *en-us*. Ensure *mycroft.conf*
    contains *\"lang\": \"en-us\"*.

## 4. Configuration {#configuration}

- *settings.json* or OVOS settings file includes:

|          |                  |                                   |
|----------|------------------|-----------------------------------|
| base_url | EMS API root URL | *http://10.33.10.109:8001/api/v1* |

## 5. Example Usage (Utterances) {#example-usage-utterances}

The following examples are based on real system outputs and correspond
to *vocab/en-us/\*.intent* patterns:

|                              |                                       |                                                                                                                                         |
|------------------------------|---------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| CompareMachines.intent       | compare two machines                  | Compressor-EU-1 consumes 72.0 kWh/hr, Compressor-1 uses 44.0 kWh/hr                                                                     |
| CheckAnomalies.intent        | are there any anomalies               | No anomalies reported right now                                                                                                         |
| ListAvailableMachines.intent | list comparable machines              | 7 machines found; 7 active (Compressor-1, Compressor-EU-1, Conveyor-A, HVAC-EU-North, HVAC-Main, Hydraulic-Pump-1, Injection-Molding-1) |
| GetEnergyData.intent         | how much energy does Compressor-1 use | Average 44.1 kWh/hr over 24 hours (25 data points)                                                                                      |

## 6. Troubleshooting {#troubleshooting}

- **Intent not matched (fallback-unknown):**

  - Confirm system language is *en-us*.
  - Check that *vocab/en-us* and *locale/en-us* directories exist.
  - Ensure the *.intent* file contains the expected phrases.
  - For slot-based phrases, verify entities in *.entity* files
    (*machine_name.entity*).
  - Clear Padatious cache and restart OVOS if necessary.

- **API 404 / Machine not found:**

  - Check *base_url* and machine names against EMS.
  - Add aliases or correct names in *.entity* files if needed.

- **Skill ID / legacy warnings:**

  - These warnings do not impact functionality.
  - Long-term recommendation: update to *create_skill(bus=\...,
    skill_id=\...)* signature.

## 7. Developer Notes {#developer-notes}

- **Intent Definitions:**
  *ovos_skill_energy_visualization/vocab/en-us/\*.intent*
- **Entities:**
  *ovos_skill_energy_visualization/vocab/en-us/machine_name.entity*
- **Handlers:** *ovos_skill_energy_visualization/\_\_init\_\_.py* (e.g.,
  *@intent_handler(\"GetEnergyData.intent\")*)
- **Bus Output:** Published under *api.response* with both summary and
  raw data.
