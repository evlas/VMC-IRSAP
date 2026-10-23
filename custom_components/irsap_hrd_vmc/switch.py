"""Piattaforma Switch per comandi IRSAP HRD VMC."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    NAME,
    REG_ESTATE_INVERNO,
    REG_ON_OFF,
    REG_ON_OFF_FASCE,
)
from .coordinator import IrsapHrdCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configura gli switch per IRSAP HRD VMC."""
    coordinator: IrsapHrdCoordinator = hass.data[DOMAIN][entry.entry_id]

    switches = [
        IrsapHrdSwitch(
            coordinator,
            entry,
            key="power",
            name="Accensione Macchina (On/Off)",
            register=REG_ON_OFF,
            icon="mdi:power",
            device_class=SwitchDeviceClass.SWITCH,
        ),
        IrsapHrdSwitch(
            coordinator,
            entry,
            key="estate_inverno",
            name="Modalità Estate / Inverno (ON=Estate, OFF=Inverno)",
            register=REG_ESTATE_INVERNO,
            icon="mdi:sun-snowflake-variant",
        ),
        IrsapHrdSwitch(
            coordinator,
            entry,
            key="regolazione_fasce",
            name="Abilitazione Fasce Orarie",
            register=REG_ON_OFF_FASCE,
            icon="mdi:calendar-clock",
        ),
    ]

    async_add_entities(switches)


class IrsapHrdSwitch(CoordinatorEntity[IrsapHrdCoordinator], SwitchEntity):
    """Rappresenta uno switch di controllo IRSAP HRD."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: IrsapHrdCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        register: int,
        icon: str,
        device_class: SwitchDeviceClass | None = None,
    ) -> None:
        """Inizializza lo switch."""
        super().__init__(coordinator)
        self.entry = entry
        self.register = register
        self._attr_name = name
        self._attr_icon = icon
        if device_class:
            self._attr_device_class = device_class
        self._attr_unique_id = f"{entry.entry_id}_switch_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=NAME,
            manufacturer="IRSAP / Dixell",
            model="HRD (iPro.GENIUS)",
            sw_version="FW 1.9",
        )

    @property
    def is_on(self) -> bool | None:
        """Restituisce lo stato corrente dello switch."""
        val = self.coordinator.data.get(self.register)
        return bool(val == 1) if val is not None else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Attiva lo switch (scrive 1)."""
        await self.coordinator.async_write_register(self.register, 1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disattiva lo switch (scrive 0)."""
        await self.coordinator.async_write_register(self.register, 0)
