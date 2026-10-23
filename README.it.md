# IRSAP HRD VMC - Integrazione Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/v/release/evlas/VMC-IRSAP?color=blue&style=flat-square)](https://github.com/evlas/VMC-IRSAP/releases)
[![Hassfest](https://github.com/evlas/VMC-IRSAP/actions/workflows/hassfest.yml/badge.svg)](https://github.com/evlas/VMC-IRSAP/actions/workflows/hassfest.yml)
[![HACS Action](https://github.com/evlas/VMC-IRSAP/actions/workflows/hacs.yml/badge.svg)](https://github.com/evlas/VMC-IRSAP/actions/workflows/hacs.yml)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-blue.svg)](https://www.home-assistant.io/)

🌐 *[English version](README.md) | Versione in italiano*

Questo repository fornisce l'integrazione completa per **Home Assistant** per il controllo e il monitoraggio delle unità di **Ventilazione Meccanica Controllata (VMC) con deumidificazione e recupero di calore IRSAP serie HRD**, dotate di controllore elettronico **Dixell iPro.GENIUS** (piattaforma Emerson / iCHiLL 200).

---

## 📋 Sintesi dell'Analisi della Documentazione

Dall'analisi dei documenti tecnici e dei registri (`Variabili Modbus HRD 2016.xls`, specifiche Modbus Dixell IC200 e immagini di quadro):

1. **Hardware di bordo**:
   - Controllore **Dixell iPro.GENIUS** (Emerson Climate Technologies).
   - Porta seriale di comunicazione **RS485**:
     - **Morsetto 63**: Segnale **`-`** (Data - / RS485 B / D-)
     - **Morsetto 64**: Segnale **`+`** (Data + / RS485 A / D+)
2. **Parametri di Comunicazione Seriale**:
   - **Protocollo**: Modbus RTU
   - **Baud Rate**: `9600` bps
   - **Data Bit**: `8`
   - **Parità**: `None` (Nessuna)
   - **Stop Bit**: `1`
   - **Indirizzo Modbus Slave predefinito**: `1`
3. **Mappatura Registri Chiave**:
   - **Temperature in decimi di grado** (`int16`, signed, fattore di scala `0.1`):
     - `0x2000` (8192): Sonda Temperatura Ripresa Ambiente
     - `0x2001` (8193): Sonda Temperatura Immissione
     - `0x2003` (8195): Sonda Temperatura Espulsione
     - `0x4500` (17664): Sonda Temperatura Aria Esterna
   - **Umidità e Qualità Aria**:
     - `0x2006` (8198): Umidità Ripresa Ambiente (% UR)
     - `0x2002` (8194): Qualità Aria (VOC / CO2)
   - **Comandi e Allarmi**:
     - `0x2035` (8245): Accensione Macchina On/Off (`0 = Spenta, 1 = Accesa`)
     - `0x2027` (8231): Modalità Stagionale (`0 = Inverno, 1 = Estate`)
     - `0x2013` (8211): Allarme Generale (`0 = Ok, 1 = In Allarme`)
   - **Regolazione Ventole**:
     - `0x2045` (8261): Velocità Rinnovo (1..3)
     - `0x2043` (8259): Velocità Espulsione (1..3)
     - `0x2046` (8262): Velocità Rinnovo in Deumidificazione/Integrazione (1..3)
   - **Setpoint**:
     - `0x2048` (8264): Setpoint Temperatura Estivo (0.1 °C)
     - `0x2054` (8276): Setpoint Temperatura Invernale (0.1 °C)
     - `0x2049` (8265): Setpoint Umidità Estivo (% UR)
     - `0x2055` (8277): Setpoint Umidità Invernale (% UR)
     - `0x2023` (8227): Differenziale Regolazione Temperatura (0.1 °C)
     - `0x2024` (8228): Differenziale Umidità (% UR)
   - **Orologio e Fasce Orarie**:
     - `0x4000` - `0x4005`: Orologio RTC di sistema (Giorno, Mese, Anno, Ora, Minuti)
     - `0xAAA0` - `0xAAAD`: Orari di inizio/fine fasce e abilitazione per giorno

---

## 🛠️ Opzioni di Integrazione Disponibili

Sono fornite tre soluzioni pronte all'uso, a seconda dell'architettura desiderata:

| Metodo | Descrizione | Requisiti | Facilità |
|---|---|---|---|
| **Metodo 1: Custom Component** | Integrazione personalizzata con interfaccia grafica (Config Flow da Home Assistant), gestione entità `climate`, `fan`, `sensor`, `binary_sensor`, `switch`, `number`. Supporta sia seriale USB che gateway TCP di rete. | Cartella `custom_components` | ⭐⭐⭐⭐⭐ (Consigliata) |
| **Metodo 2: Packages YAML Nativi** | File YAML pronti da copiare nella cartella `packages/` sfruttando l'integrazione ufficiale `modbus:` di Home Assistant (senza componenti esterni). | Solo `configuration.yaml` | ⭐⭐⭐⭐ |
| **Metodo 3: ESPHome** | Firmware per scheda ESP32 o ESP8266 + modulo ricetrasmettitore MAX485 per connettere la VMC in Wi-Fi via API nativa Home Assistant. | Modulo ESP32 + MAX485 | ⭐⭐⭐⭐ |

---

## 📦 Installazione tramite HACS (Home Assistant Community Store)

L'integrazione è strutturata nel pieno rispetto dello standard **HACS** (presenza di `hacs.json`, struttura directory `custom_components/irsap_hrd_vmc/` e `manifest.json` conforme).

### Procedura Passo-Passo per l'Installazione con HACS:

1. **Carica il repository su GitHub**:
   Se non lo hai già fatto, crea un repository su GitHub e pubblica questo progetto:
   ```bash
   git remote add origin https://github.com/TUO_UTENTE/TUO_REPOSITORY.git
   git push -u origin main --tags
   ```

2. **Aggiungi come Repository Personalizzato in HACS**:
   - Nel menù laterale di Home Assistant apri **HACS**.
   - Clicca sulla sezione **Integrazioni** (Integrations).
   - In alto a destra, clicca sui **tre puntini verticali** (`⋮`) e seleziona **Repository personalizzati** (*Custom repositories*).
   - Nel campo **Repository**, incolla l'URL del tuo repository GitHub:
     `https://github.com/TUO_UTENTE/TUO_REPOSITORY`
   - Nel menù a tendina **Tipo** (*Category*), seleziona **Integrazione** (*Integration*).
   - Clicca su **Aggiungi** (*Add*).

3. **Scarica l'Integrazione**:
   - Troverai ora la scheda **IRSAP HRD VMC** nella schermata di HACS.
   - Cliccaci sopra e premi il pulsante **Scarica** (*Download*) in basso a destra.
   - HACS scaricherà automaticamente tutti i file nella cartella `/config/custom_components/irsap_hrd_vmc/`.

4. **Riavvia Home Assistant**:
   - Vai in **Strumenti per sviluppatori** -> scheda **YAML** -> clicca su **Riavvia**.

5. **Aggiungi il Dispositivo da Interfaccia Grafica**:
   - Vai in **Impostazioni** -> **Dispositivi e Servizi** -> **Aggiungi Integrazione**.
   - Cerca **IRSAP HRD VMC**.
   - Seleziona il tipo di collegamento:
     - **Seriale RS485 diretta** (es. `/dev/ttyUSB0`, 9600 baud, slave ID 1).
     - **Gateway Modbus TCP / Wi-Fi** (es. indirizzo IP `192.168.1.100`, porta `502`, slave ID 1).
   - Conferma: tutte le entità (clima, ventole, sonde, setpoint, allarmi) saranno create automaticamente!

---

## 📄 Metodo 2: Configurazione Nativa YAML (Senza Custom Components)

Se si preferisce utilizzare l'integrazione nativa `modbus:` di Home Assistant senza installare estensioni personalizzate:

1. **Se si utilizza un adattatore USB-RS485**:
   - Copiare il file [`homeassistant_yaml/packages/irsap_hrd_modbus_serial.yaml`](file:///home/vito/Documenti/GitLocale/VMC%20IRSAP/homeassistant_yaml/packages/irsap_hrd_modbus_serial.yaml) nella cartella `/config/packages/`.
2. **Se si utilizza un gateway di rete Modbus TCP (Waveshare, Elfin, USR)**:
   - Copiare il file [`homeassistant_yaml/packages/irsap_hrd_modbus_tcp.yaml`](file:///home/vito/Documenti/GitLocale/VMC%20IRSAP/homeassistant_yaml/packages/irsap_hrd_modbus_tcp.yaml) nella cartella `/config/packages/`.
3. Nel file `configuration.yaml` verificare che i packages siano abilitati:
   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```
4. Riavviare Home Assistant.

---

## 📡 Metodo 3: Bridge Wi-Fi con ESPHome

Se la VMC non è vicina al server Home Assistant e si desidera un bridge Wi-Fi dedicato a basso costo:

1. Aprire il pannello **ESPHome**.
2. Creare un nuovo nodo e incollare il contenuto di [`esphome/irsap_hrd_bridge.yaml`](file:///home/vito/Documenti/GitLocale/VMC%20IRSAP/esphome/irsap_hrd_bridge.yaml).
3. Impostare le proprie credenziali Wi-Fi.
4. Collegare i pin UART dell'ESP32 al convertitore MAX485 e i morsetti A/B a **64 (+)** e **63 (-)** del Dixell iPro.
5. Eseguire l'upload: Home Assistant riconoscerà automaticamente la VMC via auto-discovery ESPHome.

---

## 🎨 Scheda Dashboard Lovelace

Per visualizzare e comandare la VMC con una grafica elegante e moderna:
1. Aprire una dashboard di Home Assistant -> Cliccare su **Modifica Dashboard** -> **Aggiungi Scheda** -> **Manuale**.
2. Incollare il contenuto del file [`homeassistant_yaml/dashboard/irsap_lovelace_card.yaml`](file:///home/vito/Documenti/GitLocale/VMC%20IRSAP/homeassistant_yaml/dashboard/irsap_lovelace_card.yaml).

---

## 📚 Documentazione Dettagliata
- [Documentazione Predefinita in Inglese](README.md)
- [Tabella Completa Registri Modbus (HEX & DEC)](docs/REGISTRI_MODBUS.md)
- [Guida al Collegamento Hardware e Morsetti](docs/COLLEGAMENTO_HARDWARE.md)
- [English Modbus Register Map](docs/MODBUS_REGISTERS.md)
- [English Hardware Wiring Guide](docs/HARDWARE_WIRING.md)
