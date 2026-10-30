"""Coordinator per l'aggiornamento dati Modbus dell'unità IRSAP HRD VMC."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

from pymodbus.client import AsyncModbusSerialClient, AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_BAUDRATE,
    CONF_CONNECTION_TYPE,
    CONF_HOST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    CONN_TYPE_SERIAL,
    DEFAULT_BAUDRATE,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DOMAIN,
    REG_AI_BASE,
    REG_ALLARME_GENERALE,
    REG_AO_BASE,
    REG_DI_BASE,
    REG_DIFF_REGOLAZIONE,
    REG_DIFF_UMIDITA,
    REG_ESTATE_INVERNO,
    REG_FASCIA_ORA_START_1,
    REG_ON_OFF,
    REG_ON_OFF_FASCE,
    REG_RL_BASE,
    REG_RTC_GIORNO,
    REG_SET_REG_ESTIVO,
    REG_SET_REG_INVERNALE,
    REG_SET_UMIDITA_ESTIVO,
    REG_SET_UMIDITA_INV,
    REG_TEMP_ARIA_ESTERNA,
    REG_TEMP_ESPULSIONE,
    REG_TEMP_IMMISSIONE,
    REG_TEMP_RIPRESA,
    REG_UMIDITA_RIPRESA,
    REG_VEL_ESPULSIONE,
    REG_VEL_RINNOVO,
    REG_VEL_RINNOVO_DEU,
)

_LOGGER = logging.getLogger(__name__)


def to_signed_int16(val: int | None) -> int | None:
    """Converte un valore registro a 16 bit in intero con segno."""
    if val is None:
        return None
    val = val & 0xFFFF
    return val - 0x10000 if val > 0x7FFF else val


class IrsapHrdCoordinator(DataUpdateCoordinator[dict[int, int]]):
    """Gestisce la comunicazione e la sincronizzazione dati con il Dixell iPro.GENIUS."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: dict[str, Any],
        version: str | None = None,
    ) -> None:
        """Inizializza il coordinator."""
        self.config = config
        self.version = str(version) if version is not None else "1.0.0"
        self.conn_type = config.get(CONF_CONNECTION_TYPE, CONN_TYPE_SERIAL)
        self.slave_id = int(config.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID))
        scan_interval = int(config.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

        self.client: AsyncModbusSerialClient | AsyncModbusTcpClient | None = None
        self._lock = asyncio.Lock()
        self.data: dict[int, int] = {}

    def _create_client(self) -> AsyncModbusSerialClient | AsyncModbusTcpClient:
        """Crea il client seriale o TCP per Modbus."""
        if self.conn_type == CONN_TYPE_SERIAL:
            port = self.config.get(CONF_SERIAL_PORT, "/dev/ttyUSB0")
            baudrate = int(self.config.get(CONF_BAUDRATE, DEFAULT_BAUDRATE))
            return AsyncModbusSerialClient(
                port=port,
                baudrate=baudrate,
                parity="N",
                stopbits=1,
                bytesize=8,
                timeout=2,
            )
        # TCP
        host = self.config.get(CONF_HOST, "192.168.1.100")
        port = int(self.config.get(CONF_PORT, DEFAULT_PORT))
        return AsyncModbusTcpClient(
            host=host,
            port=port,
            timeout=2,
        )

    async def _async_ensure_connected(self) -> bool:
        """Verifica che il client sia connesso, altrimenti tenta la riconnessione."""
        if self.client is None:
            self.client = self._create_client()

        if not self.client.connected:
            try:
                connected = await self.client.connect()
            except Exception as err:
                _LOGGER.error(
                    "Impossibile connettersi al controllore Modbus IRSAP HRD (%s): %s",
                    self.conn_type,
                    err,
                )
                try:
                    self.client.close()
                except Exception:
                    pass
                self.client = None
                return False

            if not connected:
                _LOGGER.error("Impossibile connettersi al controllore Modbus IRSAP HRD (%s)", self.conn_type)
                try:
                    self.client.close()
                except Exception:
                    pass
                self.client = None
                return False
        return True

    async def _read_registers(self, address: int, count: int) -> list[int] | None:
        """Legge un blocco di holding registers gestendo la compatibilità pymodbus."""
        if not await self._async_ensure_connected() or self.client is None:
            return None

        try:
            try:
                response = await self.client.read_holding_registers(
                    address=address, count=count, device_id=self.slave_id
                )
            except TypeError:
                response = await self.client.read_holding_registers(
                    address=address, count=count, slave=self.slave_id
                )

            if response is None or response.isError():
                _LOGGER.debug(
                    "Errore nella lettura dei registri partendo da 0x%04X (count=%d): %s",
                    address, count, response
                )
                return None
            return list(response.registers)
        except (ModbusException, asyncio.TimeoutError, OSError) as err:
            _LOGGER.debug("Eccezione durante lettura registri da 0x%04X: %s", address, err)
            return None

    async def _async_update_data(self) -> dict[int, int]:
        """Esegue il polling di tutti i registri della VMC IRSAP HRD."""
        async with self._lock:
            new_data = dict(self.data)
            connected = await self._async_ensure_connected()
            if not connected:
                raise UpdateFailed("Connessione Modbus fallita")

            any_read_ok = False

            # 1. Sonde di temperatura e ambiente (0x2000..0x2006, 7 registri)
            sonde = await self._read_registers(0x2000, 7)
            if sonde and len(sonde) >= 7:
                any_read_ok = True
                for idx, val in enumerate(sonde):
                    new_data[0x2000 + idx] = val
            else:
                # Fallback su registri singoli
                for reg in (REG_TEMP_RIPRESA, REG_TEMP_IMMISSIONE, REG_TEMP_ESPULSIONE, REG_UMIDITA_RIPRESA):
                    val = await self._read_registers(reg, 1)
                    if val:
                        any_read_ok = True
                        new_data[reg] = val[0]

            # 2. Allarme generale (0x2013)
            allarme = await self._read_registers(REG_ALLARME_GENERALE, 1)
            if allarme:
                any_read_ok = True
                new_data[REG_ALLARME_GENERALE] = allarme[0]

            # 3. Differenziali e Estate/Inverno (0x2023..0x2027)
            diffs = await self._read_registers(0x2023, 5)
            if diffs and len(diffs) >= 5:
                any_read_ok = True
                new_data[REG_DIFF_REGOLAZIONE] = diffs[0]
                new_data[REG_DIFF_UMIDITA] = diffs[1]
                new_data[REG_ESTATE_INVERNO] = diffs[4]
            else:
                val = await self._read_registers(REG_ESTATE_INVERNO, 1)
                if val:
                    any_read_ok = True
                    new_data[REG_ESTATE_INVERNO] = val[0]
                val = await self._read_registers(REG_DIFF_REGOLAZIONE, 1)
                if val:
                    any_read_ok = True
                    new_data[REG_DIFF_REGOLAZIONE] = val[0]

            # 4. On / Off (0x2035)
            on_off = await self._read_registers(REG_ON_OFF, 1)
            if on_off:
                any_read_ok = True
                new_data[REG_ON_OFF] = on_off[0]

            # 5. Velocità e Setpoint (0x2043..0x2055, 19 registri)
            setpoints = await self._read_registers(0x2043, 19)
            if setpoints and len(setpoints) >= 19:
                any_read_ok = True
                for idx, val in enumerate(setpoints):
                    new_data[0x2043 + idx] = val
            else:
                for reg in (
                    REG_VEL_ESPULSIONE,
                    REG_VEL_RINNOVO,
                    REG_VEL_RINNOVO_DEU,
                    REG_SET_REG_ESTIVO,
                    REG_SET_UMIDITA_ESTIVO,
                    REG_SET_REG_INVERNALE,
                    REG_SET_UMIDITA_INV,
                ):
                    val = await self._read_registers(reg, 1)
                    if val:
                        any_read_ok = True
                        new_data[reg] = val[0]

            if not any_read_ok:
                raise UpdateFailed("Nessuna risposta Modbus dall'unità IRSAP HRD")

            # 6. Sonda Aria Esterna (0x4500)
            aria_est = await self._read_registers(REG_TEMP_ARIA_ESTERNA, 1)
            if aria_est:
                new_data[REG_TEMP_ARIA_ESTERNA] = aria_est[0]

            # 7. Orologio RTC (0x4000..0x4005, 6 registri)
            rtc = await self._read_registers(REG_RTC_GIORNO, 6)
            if rtc and len(rtc) >= 6:
                for idx, val in enumerate(rtc):
                    new_data[REG_RTC_GIORNO + idx] = val

            # 8. Fasce Orarie (0xAAA0..0xAAAD, 14 registri)
            fasce = await self._read_registers(REG_FASCIA_ORA_START_1, 14)
            if fasce and len(fasce) >= 14:
                for idx, val in enumerate(fasce):
                    new_data[REG_FASCIA_ORA_START_1 + idx] = val
            else:
                on_off_fasce = await self._read_registers(REG_ON_OFF_FASCE, 1)
                if on_off_fasce:
                    new_data[REG_ON_OFF_FASCE] = on_off_fasce[0]

            # 9. Ingressi / Uscite fisiche (facoltativi)
            di_regs = await self._read_registers(REG_DI_BASE, 8)
            if di_regs:
                for idx, val in enumerate(di_regs):
                    new_data[REG_DI_BASE + idx] = val

            rl_regs = await self._read_registers(REG_RL_BASE, 8)
            if rl_regs:
                for idx, val in enumerate(rl_regs):
                    new_data[REG_RL_BASE + idx] = val

            self.data = new_data
            return self.data

    async def async_write_register(self, address: int, value: int) -> bool:
        """Scrive un singolo registro Modbus e aggiorna immediatamente lo stato locale."""
        async with self._lock:
            if not await self._async_ensure_connected() or self.client is None:
                _LOGGER.error("Scrittura non possibile: client non connesso")
                return False

            value = int(value) & 0xFFFF
            try:
                try:
                    response = await self.client.write_register(
                        address=address, value=value, device_id=self.slave_id
                    )
                except TypeError:
                    response = await self.client.write_register(
                        address=address, value=value, slave=self.slave_id
                    )

                if response is None or response.isError():
                    _LOGGER.error("Errore scrittura registro 0x%04X (valore %d): %s", address, value, response)
                    return False

                _LOGGER.debug("Scrittura registro 0x%04X eseguita con successo: %d", address, value)
                self.data[address] = value
                self.async_set_updated_data(self.data)
                return True
            except (ModbusException, asyncio.TimeoutError, OSError) as err:
                _LOGGER.error("Eccezione durante la scrittura del registro 0x%04X: %s", address, err)
                return False

    async def async_close(self) -> None:
        """Chiude la connessione Modbus."""
        if self.client is not None:
            self.client.close()
            self.client = None
