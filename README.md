# ⚡ EnMS - Energy Management System

<div align="center">

![EnMS Logo](docs/images/logo.png)

**Production-ready, open-source Energy Management System for industrial facilities**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](docker-compose.yml)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![ISO 50001](https://img.shields.io/badge/ISO-50001-orange.svg)](https://www.iso.org/iso-50001-energy-management.html)

Part of the [WASABI Project](https://wasabiproject.eu/)

</div>

---

## 🎯 Overview

EnMS is a comprehensive energy monitoring and analytics platform designed for **real-world industrial facilities**. It provides ISO 50001-compliant energy performance monitoring, machine learning-powered insights, and voice interface capabilities.

### ✨ Key Features

- **🏭 Real-time Monitoring**: Track energy consumption across all Significant Energy Users (SEUs)
- **📊 Advanced Analytics**: ML-powered baselines, forecasting, and anomaly detection
- **📈 Smart Dashboards**: Pre-built Grafana dashboards with customizable variables
- **🎤 Voice Integration**: Ready for OVOS (Open Voice OS) integration
- **🔌 Modular Architecture**: Microservices-based, API-first design
- **🐳 Zero-Touch Deployment**: Single command installation with Docker
- **🔒 Production-Ready**: Security, monitoring, and backup built-in

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NGINX (API Gateway)                       │
└────┬────────────────────────────────────────────────────┬───┘
     │                                                     │
     ▼                                                     ▼
┌─────────────────────┐                        ┌──────────────────┐
│   Unified Portal    │                        │  External APIs   │
│   Grafana           │                        │  (OVOS, etc.)    │
│   Node-RED          │                        └──────────────────┘
│   Analytics UI      │
└─────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     Core Services                            │
├──────────────┬─────────────────┬─────────────────────────────┤
│  Simulator   │    Analytics    │    Query Service            │
│  Node-RED    │    Service      │    (NLP/Voice)              │
└──────┬───────┴────────┬────────┴────────┬────────────────────┘
       │                │                 │
       └────────────────┴─────────────────┘
                        │
              ┌─────────┴─────────┐
              │   PostgreSQL +    │
              │   TimescaleDB     │
              └───────────────────┘
       ┌──────────────┬──────────────┐
       │     MQTT     │    Redis     │
       └──────────────┴──────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Linux/macOS** (Windows with WSL2)
- **4GB RAM** minimum (8GB recommended)
- **10GB disk space**

### Installation

```bash
# Clone the repository
git clone https://github.com/wasabi/enms.git
cd enms

# Copy environment template
cp .env.example .env

# Edit .env and set your passwords
nano .env

# Run the setup script
chmod +x setup.sh
./setup.sh
```

That's it! 🎉

### Access the System

After installation completes:

- **Unified Portal**: http://localhost
- **Grafana**: http://localhost:3000 (admin/your-password)
- **Node-RED**: http://localhost:1880
- **API Documentation**: http://localhost/api/docs
- **Simulator Control**: http://localhost:8003/docs

### ✨ **Automatic Dashboard Backup**

**Your Grafana changes are automatically saved every 10 minutes!**

Grafana dashboards are automatically exported to git-tracked JSON files. Just edit dashboards in the UI and commit when ready:

```bash
# 1. Edit dashboards in Grafana UI (changes auto-exported every 10 min)
# 2. Wait for next backup cycle or run manually:
./scripts/backup-grafana-dashboards.sh

# 3. Commit your changes
git add grafana/dashboards/*.json
git commit -m "Update Grafana dashboards"
git push
```

**Setup auto-backup on new systems:**
```bash
sudo ./scripts/setup-grafana-auto-backup.sh
```

For detailed information, see: [docs/GRAFANA-PERSISTENCE.md](docs/GRAFANA-PERSISTENCE.md)

> **Note**: Node-RED changes are also automatically saved to the filesystem.

---

## 📊 Data Model

### Core Entities

- **Factories**: Industrial facilities
- **Machines (SEUs)**: Significant Energy Users
- **Energy Readings**: Time-series power and energy data
- **Production Data**: Output metrics for normalization
- **Environmental Data**: Temperature, humidity, pressure

### Machine Types Supported

1. **Compressor** (1-second intervals)
2. **HVAC System** (10-second intervals)
3. **Conveyor Motor** (10-second intervals)
4. **Hydraulic Pump** (30-second intervals)
5. **Injection Molding** (30-second intervals)

---

## 🧠 Analytics & KPIs

### Key Performance Indicators

- **SEC**: Specific Energy Consumption (kWh/unit)
- **Peak Demand**: Maximum power draw (kW)
- **Load Factor**: Average/Peak ratio
- **Energy Cost**: With time-of-use tariffs
- **Carbon Intensity**: CO₂ emissions tracking

### Machine Learning Models

- **Energy Baseline (EnB)**: Multiple regression for normalization
- **Anomaly Detection**: Isolation Forest for fault detection
- **Forecasting**: ARIMA + Prophet for demand prediction

---

## 🔌 API Endpoints

### Analytics Service (Port 8001)

```
POST   /api/v1/baseline/train        # Train energy baseline model
GET    /api/v1/baseline/deviation    # Get deviation from baseline
GET    /api/v1/forecast/demand       # Get energy forecast
GET    /api/v1/anomaly/detect        # Detect anomalies
POST   /api/v1/kpi/calculate         # Calculate KPIs
```

### Query Service (Port 8002)

```
POST   /api/v1/voice/query           # Natural language query (OVOS)
GET    /api/v1/energy/machine/{id}   # Get machine energy data
GET    /api/v1/energy/machines       # Get all machines data
GET    /api/v1/production/{id}       # Get production metrics
```

### Simulator Service (Port 8003)

```
POST   /simulator/start              # Start data generation
POST   /simulator/stop               # Stop data generation
GET    /simulator/status             # Get simulator status
PUT    /simulator/config             # Update configuration
POST   /simulator/inject-anomaly     # Inject anomaly for testing
```

Full API documentation: http://localhost/api/docs

---

## 🎤 OVOS Integration

EnMS is designed to work with Open Voice OS. Example voice commands:

- *"What's the energy consumption of compressor 1 in the last hour?"*
- *"Show me machines using more than 50 kilowatts"*
- *"How is temperature affecting HVAC efficiency today?"*

### Integration Endpoint

```bash
curl -X POST http://localhost:8002/api/v1/voice/query \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "energy_consumption",
    "entities": {
      "machine": "compressor-1",
      "timeframe": "last_hour"
    }
  }'
```

See [OVOS Integration Guide](docs/ovos-integration.md) for details.

---

## 📁 Project Structure

```
enms/
├── docker-compose.yml           # Service orchestration
├── .env.example                 # Environment template
├── setup.sh                     # One-command installer
├── docs/                        # Documentation
├── nginx/                       # API Gateway config
├── portal/                      # Unified web interface
├── grafana/                     # Dashboards & provisioning
├── nodered/                     # Data pipeline flows
├── database/                    # PostgreSQL schema & init
├── simulator/                   # Factory data generator
├── analytics/                   # ML service (Python/FastAPI)
├── query-service/               # Query API (Python/FastAPI)
├── mqtt/                        # Mosquitto configuration
├── redis/                       # Redis configuration
└── scripts/                     # Utility scripts
```

---

## 🛠️ Development

### Running in Development Mode

```bash
# Use development compose file
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Enable hot-reload for services
# See docker-compose.dev.yml for configuration
```

### Running Tests

```bash
# Run all tests
./scripts/test.sh

# Run specific service tests
docker-compose exec analytics pytest
docker-compose exec query-service pytest
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f analytics
```

---

## 📈 Performance

- **Throughput**: Handles 5+ machines with 1-second intervals (5+ data points/second)
- **Storage**: TimescaleDB compression reduces storage by 90%
- **Queries**: Sub-100ms response times for dashboard queries
- **Scalability**: Horizontal scaling ready with load balancer

---

## 🔒 Security

- **Authentication**: JWT tokens for API access
- **Rate Limiting**: 100 requests/minute per IP
- **Input Validation**: Pydantic models with strict typing
- **SQL Injection**: Parameterized queries only
- **HTTPS**: SSL/TLS support (configure in nginx/ssl/)

---

## 🗄️ Backup & Recovery

### Manual Backup

```bash
./scripts/backup.sh
```

### Restore from Backup

```bash
./scripts/restore.sh backups/enms_backup_2025-10-08.sql.gz
```

### Automated Backups

Configured in `.env`:
```
BACKUP_SCHEDULE=0 3 * * *  # Daily at 3 AM
BACKUP_RETENTION_DAYS=30
```

---

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [User Guide](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Architecture Overview](docs/architecture.md)
- [OVOS Integration](docs/ovos-integration.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Contributing](CONTRIBUTING.md)

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Part of the [WASABI Project](https://wasabiproject.eu/)
- Built with [TimescaleDB](https://www.timescale.com/)
- Powered by [FastAPI](https://fastapi.tiangolo.com/)
- Visualized with [Grafana](https://grafana.com/)
- Orchestrated with [Node-RED](https://nodered.org/)

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/wasabi/enms/issues)
- **Discussions**: [GitHub Discussions](https://github.com/wasabi/enms/discussions)
- **Email**: support@wasabiproject.eu

---

## 🗺️ Roadmap

- [x] Core monitoring and dashboards
- [x] ML-powered analytics
- [x] API-first architecture
- [ ] OVOS voice integration (In Progress)
- [ ] Mobile app
- [ ] Multi-tenancy support
- [ ] Cloud deployment templates (AWS, Azure, GCP)
- [ ] Advanced predictive maintenance

---

<div align="center">

**Built with ❤️ for the industrial IoT community**

⭐ Star us on GitHub — it motivates us a lot!

</div>
