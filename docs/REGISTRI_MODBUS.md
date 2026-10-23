# Mappatura Registri Modbus - IRSAP HRD (Controllore Dixell iPro.GENIUS)

Questo documento contiene la mappatura completa dei registri Modbus RTU per le unità di ventilazione meccanica controllata con recupero di calore **IRSAP serie HRD**, dotate di controllore elettronico **Dixell iPro.GENIUS** (piattaforma iCHiLL / iPro).

---

## Parametri di Comunicazione Seriale
- **Protocollo**: Modbus RTU (Slave)
- **Supporto fisico**: Seriale RS485 (morsetti **63 [-]** e **64 [+]**)
- **Baud rate predefinito**: `9600` bps
- **Data bit**: `8`
- **Parità**: `None` (Nessuna)
- **Stop bit**: `1`
- **Indirizzo Slave predefinito**: `1` (configurabile tra 1 e 247)
- **Funzioni Modbus supportate**:
  - `0x03` (Read Holding Registers)
  - `0x06` (Write Single Register)
  - `0x10` (Write Multiple Registers)

---

## 1. Sonde di Misura e Temperatura

| Nome Segnale | Indirizzo HEX | Indirizzo DEC | Tipo | R/W | Fattore di Scala | Unità | Note / Descrizione |
|---|---|---|---|---|---|---|---|
| **Sonda Temperatura Ripresa Ambiente** | `0x2000` | **8192** | DINT (int16) | R | 0.1 | °C | Temperatura aria ambiente ripresa (es. 205 = 20.5 °C) |
| **Sonda Temperatura Immissione** | `0x2001` | **8193** | DINT (int16) | R | 0.1 | °C | Temperatura aria immessa negli ambienti |
| **Sonda Qualità Aria** | `0x2002` | **8194** | DINT (uint16)| R | 1 | ppm / idx | Valore rilevato dalla sonda VOC/CO2 |
| **Sonda Temperatura Espulsione** | `0x2003` | **8195** | DINT (int16) | R | 0.1 | °C | Temperatura aria espulsa all'esterno |
| **Sonda Umidità Ripresa Ambiente** | `0x2006` | **8198** | DINT (uint16)| R | 1 | % UR | Umidità relativa ambiente |
| **Sonda Temperatura Aria Esterna** | `0x4500` | **17664**| DINT (int16) | R | 0.1 | °C | Temperatura dell'aria esterna aspirata |

---

## 2. Setpoint e Parametri di Regolazione

| Nome Segnale | Indirizzo HEX | Indirizzo DEC | Tipo | R/W | Fattore di Scala | Unità | Note / Descrizione |
|---|---|---|---|---|---|---|---|
| **Differenziale Regolazione Estivo** | `0x2023` | **8227** | DINT (uint16)| R/W | 0.1 | °C | Isteresi regolazione temperatura in estate |
| **Differenziale Regolazione Invernale**| `0x2023` | **8227** | DINT (uint16)| R/W | 0.1 | °C | Isteresi regolazione temperatura in inverno |
| **Differenziale Umidità Estivo** | `0x2024` | **8228** | DINT (uint16)| R/W | 1 | % UR | Isteresi regolazione umidità estiva |
| **Differenziale Umidità Invernale** | `0x2024` | **8228** | DINT (uint16)| R/W | 1 | % UR | Isteresi regolazione umidità invernale |
| **Velocità Espulsione** | `0x2043` | **8259** | DINT (uint16)| R/W | 1 | - | Velocità ventola espulsione (valori ammessi: 1..3) |
| **Velocità Rinnovo** | `0x2045` | **8261** | DINT (uint16)| R/W | 1 | - | Velocità ventola immissione/rinnovo (valori: 1..3) |
| **Velocità Rinnovo in Deum./Integraz.** | `0x2046` | **8262** | DINT (uint16)| R/W | 1 | - | Velocità ventola durante deumidificazione (1..3) |
| **Set Regolazione Estivo** | `0x2048` | **8264** | DINT (int16) | R/W | 0.1 | °C | Setpoint temperatura estate (es. 240 = 24.0 °C) |
| **Set Umidità Estivo** | `0x2049` | **8265** | DINT (uint16)| R/W | 1 | % UR | Setpoint umidità estivo desiderato |
| **Set Regolazione Invernale** | `0x2054` | **8276** | DINT (int16) | R/W | 0.1 | °C | Setpoint temperatura inverno (es. 200 = 20.0 °C) |
| **Set Umidità Invernale** | `0x2055` | **8277** | DINT (uint16)| R/W | 1 | % UR | Setpoint umidità invernale desiderato |

---

## 3. Comandi di Controllo e Stato

| Nome Segnale | Indirizzo HEX | Indirizzo DEC | Tipo | R/W | Valori | Note / Descrizione |
|---|---|---|---|---|---|---|
| **Allarme Generale** | `0x2013` | **8211** | BOOL | R | 0 = Ok, 1 = In Allarme | Stato allarme generale della macchina |
| **Modalità Estate / Inverno** | `0x2027` | **8231** | BOOL | R/W | 0 = Inverno, 1 = Estate | Seleziona ciclo stagionale riscaldamento/raffrescamento |
| **Accensione / Spegnimento (On/Off)**| `0x2035` | **8245** | BOOL | R/W | 0 = Spenta, 1 = Accesa | Comando principale di accensione macchina |

---

## 4. Fasce Orarie e Orologio di Sistema (RTC)

| Nome Segnale | Indirizzo HEX | Indirizzo DEC | Tipo | R/W | Note / Descrizione |
|---|---|---|---|---|---|
| **RTC Giorno** | `0x4000` | **16384** | DINT | R | Giorno del mese (1..31) |
| **RTC Mese** | `0x4001` | **16385** | DINT | R | Mese dell'anno (1..12) |
| **RTC Anno** | `0x4002` | **16386** | DINT | R | Anno (es. 2024) |
| **RTC Ora** | `0x4003` | **16387** | DINT | R | Ora (0..23) |
| **RTC Minuti** | `0x4004` | **16388** | DINT | R | Minuti (0..59) |
| **RTC Giorno della Settimana** | `0x4005` | **16389** | DINT | R | Giorno settimanale |
| **Ora Inizio Fascia 1** | `0xAAA0` | **43680** | DINT | R/W | Ora avvio prima fascia (0..23) |
| **Ora Inizio Fascia 2** | `0xAAA1` | **43681** | DINT | R/W | Ora avvio seconda fascia |
| **Ora Inizio Fascia 3** | `0xAAA2` | **43682** | DINT | R/W | Ora avvio terza fascia |
| **Ora Fine Fascia 1** | `0xAAA3` | **43683** | DINT | R/W | Ora termine prima fascia |
| **Ora Fine Fascia 2** | `0xAAA4` | **43684** | DINT | R/W | Ora termine seconda fascia |
| **Ora Fine Fascia 3** | `0xAAA5` | **43685** | DINT | R/W | Ora termine terza fascia |
| **On/Off Regolazione Fasce Orarie** | `0xAAA6` | **43686** | BOOL | R/W | 0 = Fasce Disattive, 1 = Fasce Attive |
| **Fasce Attive Lunedì** | `0xAAA7` | **43687** | DINT | R/W | Bitmap/Valore fasce lunedì |
| **Fasce Attive Martedì** | `0xAAA8` | **43688** | DINT | R/W | Bitmap/Valore fasce martedì |
| **Fasce Attive Mercoledì** | `0xAAA9` | **43689** | DINT | R/W | Bitmap/Valore fasce mercoledì |
| **Fasce Attive Giovedì** | `0xAAAA` | **43690** | DINT | R/W | Bitmap/Valore fasce giovedì |
| **Fasce Attive Venerdì** | `0xAAAB` | **43691** | DINT | R/W | Bitmap/Valore fasce venerdì |
| **Fasce Attive Sabato** | `0xAAAC` | **43692** | DINT | R/W | Bitmap/Valore fasce sabato (nel foglio xls `AAA7C`) |
| **Fasce Attive Domenica** | `0xAAAD` | **43693** | DINT | R/W | Bitmap/Valore fasce domenica |
| **Tipologia Fascia 1** | `0x3654` | **13908** | DINT | R/W | Profilo/Modalità fascia 1 |
| **Tipologia Fascia 2** | `0x3658` | **13912** | DINT | R/W | Profilo/Modalità fascia 2 |
| **Tipologia Fascia 3** | `0x3655` | **13909** | DINT | R/W | Profilo/Modalità fascia 3 |

---

## 5. Ingressi e Uscite Fisiche

| Nome Segnale | Indirizzo HEX | Indirizzo DEC | Tipo | R/W | Note / Descrizione |
|---|---|---|---|---|---|
| **Ingressi Analogici AI01 - AI06** | `0xF000` - `0xF005` | **61440** - **61445** | DINT | R | Valori grezzi convertitori analogici |
| **Uscite Analogiche AO01 - AO04** | `0xF020` - `0xF023` | **61472** - **61475** | DINT | R | Segnali analogici 0-10V o PWM ventole/valvole |
| **Ingressi Digitali DI01 - DI08** | `0xF050` - `0xF057` | **61520** - **61527** | BOOL | R | Stato ingressi digitali (pressostati filtri, consensi, etc.) |
| **Uscite Relè RL01 - RL08** | `0xF080` - `0xF087` | **61568** - **61575** | BOOL | R | Stato relè di comando (compressore, sbrinamento, ecc.) |
