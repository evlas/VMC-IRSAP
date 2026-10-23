# Hardware Wiring Guide: Dixell iPro.GENIUS / IRSAP HRD

This document guides you through connecting the RS485 communication bus of the **Dixell iPro.GENIUS** controller on your IRSAP HRD VMC unit to **Home Assistant**.

---

## 1. Terminal Identification on Dixell iPro.GENIUS

Refer to the controller front panel (also shown in `docs/20181023_124437_1C6907C2_preview.jpeg`):

```
+-----------------------------------------------------------+
|                        iPro.GENIUS                        |
|                                                           |
|                 Remote     RS485    Ser.                  |
|                 Display     BUS     Port   [ USB ]        |
|                 Vnr + -     -   +   -   +                 |
|                [60 61 62] [63  64] [65 66]                |
+-----------------------------------------------------------+
```

### Dedicated RS485 Terminals:
- **Terminal 63**: RS485 **`-`** (also labeled as **Data -**, **B**, or **D-**)
- **Terminal 64**: RS485 **`+`** (also labeled as **Data +**, **A**, or **D+**)

> [!NOTE]
> Some RS485 adapters follow different labeling conventions for A and B. The golden rule is:
> - Terminal 64 (+) -> Data + / RS485 A / D+
> - Terminal 63 (-) -> Data - / RS485 B / D-
> If you experience communication timeouts or CRC errors, try swapping the two wires.

---

## 2. Connection Options to Home Assistant

### Option A: Direct USB - RS485 Adapter (Home Assistant on Raspberry Pi or PC/NUC)
Ideal when Home Assistant is located near the electrical panel of the VMC unit.
1. Use an industrial USB-to-RS485 converter (FTDI, CP2102, or CH340 chipset, preferably with galvanic isolation).
2. Wire connections:
   - Dixell **64 (+)** -> Adapter **A / D+**
   - Dixell **63 (-)** -> Adapter **B / D-**
   - Cable shield / GND connected to ground at one end only.
3. Plug the adapter into your Home Assistant server (recognized as `/dev/ttyUSB0` or `/dev/serial/by-id/...`).

### Option B: RS485 to Ethernet / Wi-Fi Gateway (Modbus TCP)
Ideal when the VMC unit is far from the server and local network (LAN or Wi-Fi) is available.
- Recommended models:
  - **Waveshare RS485 to RJ45 Ethernet** (POE ETH to RS485)
  - **Elfin-EW11** (Wi-Fi) or **Elfin-EE11** (Ethernet)
  - **USR-TCP232-304** / **USR-DR302**
1. Gateway serial settings:
   - Mode: **Modbus TCP** or **TCP Server / Modbus RTU over TCP**
   - Baud Rate: **9600**
   - Data Bits: **8**
   - Parity: **None**
   - Stop Bits: **1**
   - Local TCP Port: **502** (or 8899)
2. Wire connections:
   - Dixell **64 (+)** -> Gateway **A+**
   - Dixell **63 (-)** -> Gateway **B-**

### Option C: ESPHome Module (ESP32 / ESP8266 + MAX485)
Ideal for a low-cost, wireless, cloud-free integration using Home Assistant's native ESPHome API.
- Required Hardware:
  - 1x ESP32 or ESP8266 board
  - 1x 3.3V RS485 transceiver (MAX3485 or auto-direction module)
- See configuration file: `esphome/irsap_hrd_bridge.yaml`.

---

## 3. Cable and Termination Resistor
- Use shielded twisted pair cable (e.g. Belden 9841, KNX bus cable, or Cat5e/Cat6 using a twisted pair for data and the shield for drain).
- For cable lengths exceeding 20-30 meters (65-100 ft), add a **120 Ω termination resistor** between terminals 63 and 64 at the end of the line.
