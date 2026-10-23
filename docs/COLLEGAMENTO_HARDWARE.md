# Guida al Collegamento Hardware: Dixell iPro.GENIUS / IRSAP HRD

Questo documento illustra come effettuare il collegamento fisico del bus di comunicazione RS485 tra il controllore **Dixell iPro.GENIUS** a bordo dell'unità VMC IRSAP HRD e il sistema **Home Assistant**.

---

## 1. Identificazione dei Morsetti sul Dixell iPro.GENIUS

Facendo riferimento al pannello frontale del controllore Dixell (visibile nell'immagine del quadro):

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

### Morsetti RS485 dedicati:
- **Morsetto 63**: Segnale RS485 **`-`** (noto anche come **Data -**, **B** oppure **D-**)
- **Morsetto 64**: Segnale RS485 **`+`** (noto anche come **Data +**, **A** oppure **D+**)

> [!NOTE]
> La convenzione delle etichette dei convertitori RS485 talvolta inverte A/B. La regola fondamentale è:
> - Morsetto 64 (+) -> Data + / RS485 A / D+
> - Morsetto 63 (-) -> Data - / RS485 B / D-
> Se si verificano errori di timeout o mancata risposta (CRC Error), provare a invertire la polarità tra i due fili.

---

## 2. Tipologie di Collegamento verso Home Assistant

Sono possibili tre opzioni di connessione:

### Opzione A: Adattatore USB - RS485 diretto (Home Assistant su Raspberry Pi o PC/NUC)
Ideale se il server Home Assistant si trova vicino al quadro elettrico della VMC.
1. Utilizzare un convertitore industriale **USB-RS485** con chip FTDI, CP2102 o CH340 (preferibilmente con isolamento galvanico).
2. Collegare:
   - Morsetto **64 (+)** del Dixell al morsetto **A / D+** dell'adattatore USB.
   - Morsetto **63 (-)** del Dixell al morsetto **B / D-** dell'adattatore USB.
   - La schermatura del cavo (GND) a terra solo da un lato.
3. Inserire l'adattatore nella porta USB del server Home Assistant (verrà rilevato come `/dev/ttyUSB0` o `/dev/serial/by-id/...`).

### Opzione B: Gateway Seriale RS485 - Ethernet / Wi-Fi (Modbus TCP)
Ideale se la VMC è distante dal server Home Assistant e si dispone di rete LAN o Wi-Fi.
- Modelli consigliati:
  - **Waveshare RS485 to RJ45 Ethernet** (es. POE ETH to RS485)
  - **Elfin-EW11** (Wi-Fi) o **Elfin-EE11** (Ethernet)
  - **USR-TCP232-304** / **USR-DR302**
1. Configurazione del gateway:
   - Protocollo: **Modbus TCP** oppure **TCP Server / Modbus RTU Over TCP**
   - Baud rate: **9600**
   - Data bits: **8**
   - Parity: **None**
   - Stop bits: **1**
   - Porta locale TCP tipica: **502** (o 8899)
2. Collegamento:
   - Dixell **64 (+)** -> Morsetto **A+** del gateway
   - Dixell **63 (-)** -> Morsetto **B-** del gateway

### Opzione C: Modulo ESPHome (ESP32 / ESP8266 + MAX485)
Ideale per integrare la VMC via Wi-Fi direttamente nell'ecosistema Home Assistant tramite l'integrazione nativa ESPHome.
- Hardware richiesto:
  - 1x Scheda ESP32 (o ESP8266 Wemos D1 Mini)
  - 1x Modulo ricetrasmettitore RS485 a 3.3V (es. MAX3485 o scheda RS485 con auto direction control)
  - Alimentatore 5V / 3.3V
- Vedere il file dedicato `esphome/irsap_hrd_bridge.yaml`.

---

## 3. Cavo e Resistenza di Terminazione
- Utilizzare un cavo schermato a coppia intrecciata (**Twisted Pair**, ad esempio cavo Belden 9841, cavo bus KNX o cavo Cat5e/Cat6 sfruttando una coppia per i dati e la calza per lo schermo).
- Per tratte superiori a 20-30 metri, aggiungere una **resistenza di terminazione da 120 Ω** tra i morsetti 63 e 64 all'estremità della linea.
