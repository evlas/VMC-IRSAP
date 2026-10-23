"""Costanti per l'integrazione IRSAP HRD VMC (Dixell iPro.GENIUS)."""

from homeassistant.const import Platform

DOMAIN = "irsap_hrd_vmc"
NAME = "IRSAP HRD VMC"

PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
    Platform.FAN,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
]

# Chiavi di configurazione
CONF_CONNECTION_TYPE = "connection_type"
CONF_SERIAL_PORT = "serial_port"
CONF_BAUDRATE = "baudrate"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_SLAVE_ID = "slave_id"
CONF_SCAN_INTERVAL = "scan_interval"

CONN_TYPE_SERIAL = "serial"
CONN_TYPE_TCP = "tcp"

DEFAULT_BAUDRATE = 9600
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1
DEFAULT_SCAN_INTERVAL = 15

# Registri Modbus (Indirizzi Decimali ed Esadecimali)
# Sonde
REG_TEMP_RIPRESA = 0x2000      # 8192 - Sonda Temperatura Ripresa Ambiente (0.1 °C, signed)
REG_TEMP_IMMISSIONE = 0x2001   # 8193 - Sonda Immissione (0.1 °C, signed)
REG_QUALITA_ARIA = 0x2002      # 8194 - Sonda Qualità aria
REG_TEMP_ESPULSIONE = 0x2003   # 8195 - Sonda Espulsione (0.1 °C, signed)
REG_UMIDITA_RIPRESA = 0x2006   # 8198 - Sonda Umidita Ripresa Ambiente (% UR)
REG_TEMP_ARIA_ESTERNA = 0x4500 # 17664 - Sonda Aria Esterna (0.1 °C, signed)

# Allarmi e Comandi
REG_ALLARME_GENERALE = 0x2013  # 8211 - Allarme Generale (0=Ok, 1=Allarme)
REG_DIFF_REGOLAZIONE = 0x2023  # 8227 - Differenziale Regolazione Estivo/Invernale (0.1 °C)
REG_DIFF_UMIDITA = 0x2024      # 8228 - Differenziale umidità Estivo/Invernale (% UR)
REG_ESTATE_INVERNO = 0x2027    # 8231 - Estate/Inverno (0=Inverno, 1=Estate)
REG_ON_OFF = 0x2035            # 8245 - On/Off (0=Spenta, 1=Accesa)

# Ventilazione e Setpoint
REG_VEL_ESPULSIONE = 0x2043    # 8259 - Set velocità espulsione (1..3)
REG_VEL_RINNOVO = 0x2045       # 8261 - Set velocità rinnovo (1..3)
REG_VEL_RINNOVO_DEU = 0x2046   # 8262 - Set velocità rinnovo in deu/int (1..3)
REG_SET_REG_ESTIVO = 0x2048    # 8264 - Set Regolazione Estivo (0.1 °C, signed)
REG_SET_UMIDITA_ESTIVO = 0x2049# 8265 - Set umidità Estivo (% UR)
REG_SET_REG_INVERNALE = 0x2054 # 8276 - Set Regolazione Invernale (0.1 °C, signed)
REG_SET_UMIDITA_INV = 0x2055   # 8277 - Set umidità Invernale (% UR)

# Orologio (RTC)
REG_RTC_GIORNO = 0x4000        # 16384 - Giorno
REG_RTC_MESE = 0x4001          # 16385 - Mese
REG_RTC_ANNO = 0x4002          # 16386 - Anno
REG_RTC_ORA = 0x4003           # 16387 - Ora
REG_RTC_MINUTI = 0x4004        # 16388 - Minuti
REG_RTC_DAYWEEK = 0x4005       # 16389 - Giorno settimana

# Fasce Orarie
REG_FASCIA_ORA_START_1 = 0xAAA0# 43680
REG_FASCIA_ORA_START_2 = 0xAAA1# 43681
REG_FASCIA_ORA_START_3 = 0xAAA2# 43682
REG_FASCIA_ORA_STOP_1 = 0xAAA3 # 43683
REG_FASCIA_ORA_STOP_2 = 0xAAA4 # 43684
REG_FASCIA_ORA_STOP_3 = 0xAAA5 # 43685
REG_ON_OFF_FASCE = 0xAAA6      # 43686 - OnOff Regolazione su fasce orarie
REG_FASCE_LUN = 0xAAA7         # 43687
REG_FASCE_MAR = 0xAAA8         # 43688
REG_FASCE_MER = 0xAAA9         # 43689
REG_FASCE_GIO = 0xAAAA         # 43690
REG_FASCE_VEN = 0xAAAB         # 43691
REG_FASCE_SAB = 0xAAAC         # 43692
REG_FASCE_DOM = 0xAAAD         # 43693
REG_TIPOLOGIA_FASCIA_1 = 0x3654# 13908
REG_TIPOLOGIA_FASCIA_2 = 0x3658# 13912
REG_TIPOLOGIA_FASCIA_3 = 0x3655# 13909

# Ingressi / Uscite fisiche
REG_AI_BASE = 0xF000           # 61440 - AI01..AI06 (6 registri)
REG_AO_BASE = 0xF020           # 61472 - AO01..AO04 (4 registri)
REG_DI_BASE = 0xF050           # 61520 - DI01..DI08 (8 registri)
REG_RL_BASE = 0xF080           # 61568 - RL01..RL08 (8 registri)
