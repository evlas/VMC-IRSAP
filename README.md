# IRSAP HRD VMC - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/v/release/evlas/VMC-IRSAP?color=blue&style=flat-square)](https://github.com/evlas/VMC-IRSAP/releases)
[![Hassfest](https://github.com/evlas/VMC-IRSAP/actions/workflows/hassfest.yml/badge.svg)](https://github.com/evlas/VMC-IRSAP/actions/workflows/hassfest.yml)
[![HACS Action](https://github.com/evlas/VMC-IRSAP/actions/workflows/hacs.yml/badge.svg)](https://github.com/evlas/VMC-IRSAP/actions/workflows/hacs.yml)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-blue.svg)](https://www.home-assistant.io/)

🌐 *English | [Versione in italiano](README.it.md)*

This repository provides a complete **Home Assistant** integration for monitoring and controlling **IRSAP HRD series** heat recovery and dehumidification mechanical ventilation units (VMC), powered by the **Dixell iPro.GENIUS** controller (Emerson Climate Technologies).

---

## 📋 Technical Analysis Summary

From official technical documents and Modbus mapping sheets (`Variabili Modbus HRD 2016.xls`, Dixell IC200 Modbus specs, and electrical cabinet photos):

1. **Hardware Controller**:
   - **Dixell iPro.GENIUS** (Emerson Climate Technologies).
   - **RS485 Serial Communication**:
     - **Terminal 63**: `RS485 -` (Data - / B / D-)
     - **Terminal 64**: `RS485 +` (Data + / A / D+)
2. **Serial Communication Settings**:
   - **Protocol**: Modbus RTU
   - **Baud Rate**: `9600` bps
   - **Data Bits**: `8`
   - **Parity**: `None`
   - **Stop Bits**: `1`
   - **Default Slave ID**: `1`
3. **Key Registers**:
   - **Temperature Probes** (`int16`, signed, 0.1 °C scale):
     - `0x2000` (8192): Ambient Return Air Temperature
     - `0x2001` (8193): Supply Air Temperature
     - `0x2003` (8195): Exhaust Air Temperature
     - `0x4500` (17664): Outdoor Air Intake Temperature
   - **Humidity & Air Quality**:
     - `0x2006` (8198): Ambient Return Air Humidity (% RH)
     - `0x2002` (8194): Air Quality Probe (VOC / CO2 index)
   - **Commands & Alarms**:
     - `0x2035` (8245): Power On / Off (`0 = Off, 1 = On`)
     - `0x2027` (8231): Seasonal Mode (`0 = Winter, 1 = Summer`)
     - `0x2013` (8211): General Alarm (`0 = OK, 1 = In Alarm`)
   - **Fan Speed Control**:
     - `0x2045` (8261): Supply (Renewal) Fan Speed (1..3)
     - `0x2043` (8259): Exhaust Fan Speed (1..3)
     - `0x2046` (8262): Dehumidification Renewal Speed (1..3)
   - **Setpoints & Differentials**:
     - `0x2048` (8264): Summer Temperature Setpoint (0.1 °C)
     - `0x2054` (8276): Winter Temperature Setpoint (0.1 °C)
     - `0x2049` (8265): Summer Humidity Setpoint (% RH)
     - `0x2055` (8277): Winter Humidity Setpoint (% RH)
     - `0x2023` (8227): Temperature Regulation Differential (0.1 °C)
     - `0x2024` (8228): Humidity Regulation Differential (% RH)

---

## 📦 Installation via HACS (Recommended)

This integration is fully compliant with **HACS** (*Home Assistant Community Store*).

### Step-by-Step Installation:

1. **Add Custom Repository in HACS**:
   - In Home Assistant, open **HACS** from the left sidebar.
   - Go to **Integrations**.
   - In the top-right corner, click the three vertical dots (`⋮`) and select **Custom repositories**.
   - In the **Repository** field, paste:
     ```text
     https://github.com/evlas/VMC-IRSAP
     ```
   - In the **Category** dropdown, select **Integration**.
   - Click **Add**.

2. **Download the Integration**:
   - Locate the **IRSAP HRD VMC** card and click **Download**.
   - HACS automatically places the integration inside `/config/custom_components/irsap_hrd_vmc/`.

3. **Restart Home Assistant**:
   - Go to **Developer Tools** -> **YAML** -> click **Restart**.

4. **Add the Device via UI**:
   - Go to **Settings** -> **Devices & Services** -> **Add Integration**.
   - Search for **IRSAP HRD VMC**.
   - Choose your connection type:
     - **Direct RS485 Serial** (e.g. `/dev/ttyUSB0`, 9600 baud, Slave ID 1).
     - **Modbus TCP / Wi-Fi Gateway** (e.g. Waveshare, Elfin-EW11, USR, or ESP32 bridge at `192.168.1.100:502`).
   - Confirm: All climate, fan, sensor, switch, number, and binary sensor entities are automatically created!

---

## 📄 Alternative Methods

### Method 2: Native Home Assistant YAML Packages (No Custom Components)
- For USB-RS485: Use [`homeassistant_yaml/packages/irsap_hrd_modbus_serial.yaml`](homeassistant_yaml/packages/irsap_hrd_modbus_serial.yaml).
- For Modbus TCP gateways: Use [`homeassistant_yaml/packages/irsap_hrd_modbus_tcp.yaml`](homeassistant_yaml/packages/irsap_hrd_modbus_tcp.yaml).
- Copy the file to `/config/packages/` and verify `packages: !include_dir_named packages` is in your `configuration.yaml`.

### Method 3: ESPHome Wireless Bridge
- Use an ESP32 or ESP8266 + MAX485 board loaded with [`esphome/irsap_hrd_bridge.yaml`](esphome/irsap_hrd_bridge.yaml).
- Connect directly to Dixell terminals 64 (+) and 63 (-).
- Zero cloud, 100% local Home Assistant auto-discovery.

---

## 🎨 Lovelace Dashboard Card
A pre-configured Lovelace dashboard card is provided in [`homeassistant_yaml/dashboard/irsap_lovelace_card.yaml`](homeassistant_yaml/dashboard/irsap_lovelace_card.yaml).

---

## 📚 Detailed Documentation
- [English Modbus Register Map (HEX & DEC)](docs/MODBUS_REGISTERS.md)
- [English Hardware Wiring Guide](docs/HARDWARE_WIRING.md)
- [Mappa Registri Modbus in Italiano](docs/REGISTRI_MODBUS.md)
- [Guida Collegamento Hardware in Italiano](docs/COLLEGAMENTO_HARDWARE.md)
- [Documentazione Completa in Italiano](README.it.md)
