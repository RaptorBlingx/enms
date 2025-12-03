    # Factory Requirements for EnMS Implementation (WASABI Project)

    ---

    ## 1. Executive Summary
    We are deploying an AI-powered Energy Management System (EnMS) compliant with ISO 50001. To ensure a successful pilot, we need specific hardware, connectivity, and data from your factory.

    **Our Core Expectation:** The factory must treat its machines as data sources that can transmit readings to a central point (MQTT Broker).

    ---

    ## 2. Minimum Requirements (Must Have)

    ### A. Energy Metering Infrastructure
    We need to measure the energy consumption of your **Significant Energy Users (SEUs)** (e.g., main compressors, chillers, furnaces, or large production lines).
    *   **Requirement:** Digital Energy Meters installed on key machines.
    *   **Data Variables:** Must measure **Active Power (kW)** and **Active Energy (kWh)**.
    *   **Connectivity:** Meters must be connected to a network (Modbus TCP, Modbus RTU via Gateway, or MQTT).

    ### B. IT Infrastructure & Server
    *   **Server Hardware:** A dedicated PC or Server to run the EnMS software (Docker).
        *   *Spec:* Intel i5/i7 or equivalent, 16GB RAM, 256GB SSD.
        *   *OS:* Ubuntu Linux 22.04 LTS (preferred) or Windows.
        *   *Why?* This ensures your data stays local and the Voice Assistant responds instantly.
    *   **Internet Connection:** Stable connection for remote software deployment and updates.
    *   **Local Network (LAN):** All meters and the server must be on the same local network.

    ### C. Production Data (Crucial for ISO 50001)
    To calculate energy efficiency (not just consumption), we need to know **what** the factory produced.
    *   **Requirement:** A way to count production output.
    *   **Data Variables:** `Production Count` (units made) OR `Machine Status` (Running/Idle).
    *   **Why?** If a machine uses 100kW but produces 0 units, that is an anomaly. Without this, we cannot calculate efficiency.

    ---

    ## 3. Good-to-Have Requirements (For Advanced AI)

    These are not strictly mandatory to start, but they enable the advanced AI/ML features:

    ### A. Environmental & Process Sensors
    *   **Context Data:** `Outdoor Temperature`, `Humidity`, or specific process variables (e.g., `Oven Temperature`).
    *   **Why?** The AI needs this to distinguish between "Winter heating load" and "Machine fault".

    ### B. Digital Integration (MQTT)
    *   **Edge Gateway:** Ideally, you have a gateway that can **PUBLISH** JSON messages to an MQTT Broker.
    *   **Why?** This is the fastest way to integrate. If you don't have this, we will use Node-RED to read your Modbus meters directly.

    ---

    ## 4. Installation & Implementation Phase Expectations

    ### Phase 1: Preparation (Before we arrive)
    *   **Hardware:** Install necessary energy meters on the agreed machines.
    *   **Network:** Provide network cabling to the meters and server location.
    *   **Personnel:** Designate a "Technical Point of Contact" (Maintenance or IT) who knows the factory network.

    ### Phase 2: Installation (Day 1-2)
    *   **Access:** Grant us remote access (e.g. VPN Tunnel) to the dedicated server.
    *   **Mapping:** Assist us in identifying machines: "Meter ID 101 corresponds to Compressor #2".
    *   **Data Validation:** Help us verify that the numbers we see on the dashboard match the physical machine displays.

    ### Phase 3: Implementation (Week 1)
    *   **Usage:** Staff should start using the dashboards for daily monitoring.
    *   **Feedback:** Share any unexpected issues so we can work on it together.