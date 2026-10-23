"""Config Flow per l'integrazione IRSAP HRD VMC."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_BAUDRATE,
    CONF_CONNECTION_TYPE,
    CONF_HOST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    CONN_TYPE_SERIAL,
    CONN_TYPE_TCP,
    DEFAULT_BAUDRATE,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class IrsapHrdConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestisce il Config Flow per IRSAP HRD VMC."""

    VERSION = 1

    def __init__(self) -> None:
        """Inizializza lo stato del flusso."""
        self.conn_type: str = CONN_TYPE_SERIAL

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Primo step: selezione del tipo di connessione (Seriale o TCP)."""
        if user_input is not None:
            self.conn_type = user_input[CONF_CONNECTION_TYPE]
            if self.conn_type == CONN_TYPE_SERIAL:
                return await self.async_step_serial()
            return await self.async_step_tcp()

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_CONNECTION_TYPE, default=CONN_TYPE_SERIAL
                ): vol.In(
                    {
                        CONN_TYPE_SERIAL: "Seriale RS485 diretta (USB-RS485)",
                        CONN_TYPE_TCP: "Gateway Modbus TCP / Wi-Fi (Waveshare, Elfin, USR, ESPHome)",
                    }
                )
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_serial(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configurazione connessione seriale RS485."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(f"irsap_vmc_serial_{user_input[CONF_SERIAL_PORT]}")
            self._abort_if_unique_id_configured()

            data = {
                CONF_CONNECTION_TYPE: CONN_TYPE_SERIAL,
                CONF_SERIAL_PORT: user_input[CONF_SERIAL_PORT],
                CONF_BAUDRATE: user_input[CONF_BAUDRATE],
                CONF_SLAVE_ID: user_input[CONF_SLAVE_ID],
                CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
            }
            return self.async_create_entry(
                title=f"IRSAP HRD ({user_input[CONF_SERIAL_PORT]})",
                data=data,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_SERIAL_PORT, default="/dev/ttyUSB0"): str,
                vol.Required(CONF_BAUDRATE, default=DEFAULT_BAUDRATE): vol.In(
                    [4800, 9600, 19200, 38400, 57600, 115200]
                ),
                vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=247)
                ),
                vol.Required(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
            }
        )

        return self.async_show_form(step_id="serial", data_schema=schema, errors=errors)

    async def async_step_tcp(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configurazione connessione TCP / Ethernet / Wi-Fi."""
        errors: dict[str, str] = {}

        if user_input is not None:
            unique_id = f"irsap_vmc_tcp_{user_input[CONF_HOST]}_{user_input[CONF_PORT]}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            data = {
                CONF_CONNECTION_TYPE: CONN_TYPE_TCP,
                CONF_HOST: user_input[CONF_HOST],
                CONF_PORT: user_input[CONF_PORT],
                CONF_SLAVE_ID: user_input[CONF_SLAVE_ID],
                CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
            }
            return self.async_create_entry(
                title=f"IRSAP HRD ({user_input[CONF_HOST]}:{user_input[CONF_PORT]})",
                data=data,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default="192.168.1.100"): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=65535)
                ),
                vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=247)
                ),
                vol.Required(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
            }
        )

        return self.async_show_form(step_id="tcp", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Restituisce il flusso delle opzioni."""
        return IrsapHrdOptionsFlowHandler(config_entry)


class IrsapHrdOptionsFlowHandler(config_entries.OptionsFlow):
    """Gestisce la modifica delle opzioni dell'integrazione."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Inizializza l'handler delle opzioni."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Gestisce le opzioni modificabili."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}
        conn_type = current.get(CONF_CONNECTION_TYPE, CONN_TYPE_SERIAL)

        fields: dict[Any, Any] = {
            vol.Required(
                CONF_SLAVE_ID, default=current.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=247)),
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=current.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
        }

        if conn_type == CONN_TYPE_TCP:
            fields[
                vol.Required(
                    CONF_HOST, default=current.get(CONF_HOST, "192.168.1.100")
                )
            ] = str
            fields[
                vol.Required(CONF_PORT, default=current.get(CONF_PORT, DEFAULT_PORT))
            ] = vol.All(vol.Coerce(int), vol.Range(min=1, max=65535))
        else:
            fields[
                vol.Required(
                    CONF_SERIAL_PORT,
                    default=current.get(CONF_SERIAL_PORT, "/dev/ttyUSB0"),
                )
            ] = str
            fields[
                vol.Required(
                    CONF_BAUDRATE,
                    default=current.get(CONF_BAUDRATE, DEFAULT_BAUDRATE),
                )
            ] = vol.In([4800, 9600, 19200, 38400, 57600, 115200])

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(fields),
        )
