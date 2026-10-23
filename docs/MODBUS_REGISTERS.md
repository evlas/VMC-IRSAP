# Modbus Register Map - IRSAP HRD (Dixell iPro.GENIUS Controller)

This document contains the complete Modbus RTU register mapping for **IRSAP HRD series** mechanical ventilation units with heat recovery and dehumidification, equipped with the **Dixell iPro.GENIUS** electronic controller (Emerson / iCHiLL platform).

---

## Serial Communication Parameters
- **Protocol**: Modbus RTU (Slave)
- **Physical layer**: RS485 Serial (terminals **63 [-]** and **64 [+]**)
- **Default Baud Rate**: `9600` bps
- **Data Bits**: `8`
- **Parity**: `None`
- **Stop Bits**: `1`
- **Default Slave Address**: `1` (configurable from 1 to 247)
- **Supported Modbus Functions**:
  - `0x03` (Read Holding Registers)
  - `0x06` (Write Single Register)
  - `0x10` (Write Multiple Registers)

---

## 1. Sensors and Temperature Probes

| Signal Name | HEX Address | DEC Address | Type | R/W | Scale Factor | Unit | Description / Notes |
|---|---|---|---|---|---|---|---|
| **Room Return Temperature Probe** | `0x2000` | **8192** | DINT (int16) | R | 0.1 | °C | Ambient room return air temperature (e.g. 205 = 20.5 °C) |
| **Supply Air Temperature Probe** | `0x2001` | **8193** | DINT (int16) | R | 0.1 | °C | Fresh air temperature supplied into rooms |
| **Air Quality Probe** | `0x2002` | **8194** | DINT (uint16)| R | 1 | ppm / idx | VOC / CO2 air quality probe value |
| **Exhaust Air Temperature Probe** | `0x2003` | **8195** | DINT (int16) | R | 0.1 | °C | Stale air temperature expelled outside |
| **Room Return Humidity Probe** | `0x2006` | **8198** | DINT (uint16)| R | 1 | % RH | Ambient relative humidity |
| **Outdoor Air Temperature Probe** | `0x4500` | **17664**| DINT (int16) | R | 0.1 | °C | Fresh outdoor intake air temperature |

---

## 2. Setpoints and Regulation Parameters

| Signal Name | HEX Address | DEC Address | Type | R/W | Scale Factor | Unit | Description / Notes |
|---|---|---|---|---|---|---|---|
| **Summer Regulation Differential** | `0x2023` | **8227** | DINT (uint16)| R/W | 0.1 | °C | Temperature regulation hysteresis in summer |
| **Winter Regulation Differential** | `0x2023` | **8227** | DINT (uint16)| R/W | 0.1 | °C | Temperature regulation hysteresis in winter |
| **Summer Humidity Differential** | `0x2024` | **8228** | DINT (uint16)| R/W | 1 | % RH | Humidity hysteresis in summer |
| **Winter Humidity Differential** | `0x2024` | **8228** | DINT (uint16)| R/W | 1 | % RH | Humidity hysteresis in winter |
| **Exhaust Fan Speed** | `0x2043` | **8259** | DINT (uint16)| R/W | 1 | - | Exhaust fan speed level (allowed: 1..3) |
| **Renewal (Supply) Fan Speed** | `0x2045` | **8261** | DINT (uint16)| R/W | 1 | - | Fresh air supply fan speed level (allowed: 1..3) |
| **Dehumidification Renewal Speed** | `0x2046` | **8262** | DINT (uint16)| R/W | 1 | - | Supply fan speed during dehumidification (1..3) |
| **Summer Temperature Setpoint** | `0x2048` | **8264** | DINT (int16) | R/W | 0.1 | °C | Summer target temperature (e.g. 240 = 24.0 °C) |
| **Summer Humidity Setpoint** | `0x2049` | **8265** | DINT (uint16)| R/W | 1 | % RH | Summer desired relative humidity target |
| **Winter Temperature Setpoint** | `0x2054` | **8276** | DINT (int16) | R/W | 0.1 | °C | Winter target temperature (e.g. 200 = 20.0 °C) |
| **Winter Humidity Setpoint** | `0x2055` | **8277** | DINT (uint16)| R/W | 1 | % RH | Winter desired relative humidity target |

---

## 3. Control Commands and Status

| Signal Name | HEX Address | DEC Address | Type | R/W | Values | Description / Notes |
|---|---|---|---|---|---|---|
| **General Alarm** | `0x2013` | **8211** | BOOL | R | 0 = Normal, 1 = In Alarm | Unit general alarm indicator |
| **Summer / Winter Mode** | `0x2027` | **8231** | BOOL | R/W | 0 = Winter, 1 = Summer | Seasonal heating/cooling mode selection |
| **Power On / Off** | `0x2035` | **8245** | BOOL | R/W | 0 = Off, 1 = On | Main unit power switch |

---

## 4. Time Schedules and Real-Time Clock (RTC)

| Signal Name | HEX Address | DEC Address | Type | R/W | Description / Notes |
|---|---|---|---|---|---|
| **RTC Day** | `0x4000` | **16384** | DINT | R | Day of the month (1..31) |
| **RTC Month** | `0x4001` | **16385** | DINT | R | Month of the year (1..12) |
| **RTC Year** | `0x4002` | **16386** | DINT | R | Year (e.g. 2024) |
| **RTC Hour** | `0x4003` | **16387** | DINT | R | Hour (0..23) |
| **RTC Minute** | `0x4004` | **16388** | DINT | R | Minute (0..59) |
| **RTC Day of Week** | `0x4005` | **16389** | DINT | R | Day of the week (1=Mon..7=Sun) |
| **Time Band 1 Start Hour** | `0xAAA0` | **43680** | DINT | R/W | Slot 1 start hour (0..23) |
| **Time Band 2 Start Hour** | `0xAAA1` | **43681** | DINT | R/W | Slot 2 start hour |
| **Time Band 3 Start Hour** | `0xAAA2` | **43682** | DINT | R/W | Slot 3 start hour |
| **Time Band 1 Stop Hour** | `0xAAA3` | **43683** | DINT | R/W | Slot 1 end hour |
| **Time Band 2 Stop Hour** | `0xAAA4` | **43684** | DINT | R/W | Slot 2 end hour |
| **Time Band 3 Stop Hour** | `0xAAA5` | **43685** | DINT | R/W | Slot 3 end hour |
| **Time Schedule Enable (On/Off)** | `0xAAA6` | **43686** | BOOL | R/W | 0 = Disabled, 1 = Enabled |
| **Active Bands Monday** | `0xAAA7` | **43687** | DINT | R/W | Schedule bitmap for Monday |
| **Active Bands Tuesday** | `0xAAA8` | **43688** | DINT | R/W | Schedule bitmap for Tuesday |
| **Active Bands Wednesday** | `0xAAA9` | **43689** | DINT | R/W | Schedule bitmap for Wednesday |
| **Active Bands Thursday** | `0xAAAA` | **43690** | DINT | R/W | Schedule bitmap for Thursday |
| **Active Bands Friday** | `0xAAAB` | **43691** | DINT | R/W | Schedule bitmap for Friday |
| **Active Bands Saturday** | `0xAAAC` | **43692** | DINT | R/W | Schedule bitmap for Saturday |
| **Active Bands Sunday** | `0xAAAD` | **43693** | DINT | R/W | Schedule bitmap for Sunday |
| **Time Band 1 Type** | `0x3654` | **13908** | DINT | R/W | Profile/Mode for slot 1 |
| **Time Band 2 Type** | `0x3658` | **13912** | DINT | R/W | Profile/Mode for slot 2 |
| **Time Band 3 Type** | `0x3655` | **13909** | DINT | R/W | Profile/Mode for slot 3 |

---

## 5. Physical Inputs and Outputs

| Signal Name | HEX Address | DEC Address | Type | R/W | Description / Notes |
|---|---|---|---|---|---|
| **Analog Inputs AI01 - AI06** | `0xF000` - `0xF005` | **61440** - **61445** | DINT | R | Raw ADC values |
| **Analog Outputs AO01 - AO04** | `0xF020` - `0xF023` | **61472** - **61475** | DINT | R | 0-10V / PWM control signals for fans and valves |
| **Digital Inputs DI01 - DI08** | `0xF050` - `0xF057` | **61520** - **61527** | BOOL | R | Digital inputs (filter pressure switches, interlocks) |
| **Relay Outputs RL01 - RL08** | `0xF080` - `0xF087` | **61568** - **61575** | BOOL | R | Relay states (compressor, defrost, alarms) |
