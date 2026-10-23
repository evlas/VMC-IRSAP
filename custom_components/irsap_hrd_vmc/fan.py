"""Piattaforma Fan per il controllo delle ventole di IRSAP HRD VMC."""

from __future__ import annotations

import math
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.percentage import (
    int_states_in_range,
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .const import (
    DOMAIN,
    NAME,
    REG_ON_OFF,
    REG_VEL_ESPULSIONE,
    REG_VEL_RINNOVO,
    REG_VEL_RINNOVO_DEU,
)
from .coordinator import IrsapHrdCoordinator

SPEED_RANGE = (1, 3)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configura le entità Fan per IRSAP HRD."""
    coordinator: IrsapHrdCoordinator = hass.data[DOMAIN][entry.entry_id]

    fans = [
        IrsapHrdFan(
            coordinator,
            entry,
            key="rinnovo",
            name="Ventola Rinnovo (Immissione)",
            speed_register=REG_VEL_RINNOVO,
            icon="mdi:fan",
        ),
        IrsapHrdFan(
            coordinator,
            entry,
            key="espulsione",
            name="Ventola Espulsione",
            speed_register=REG_VEL_ESPULSIONE,
            icon="mdi:fan-chevron-up",
        ),
        IrsapHrdFan(
            coordinator,
            entry,
            key="rinnovo_deu",
            name="Ventola Rinnovo in Deumidificazione",
            speed_register=REG_VEL_RINNOVO_DEU,
            icon="mdi:fan-auto",
        ),
    ]
    async_add_entities(fans)


class IrsapHrdFan(CoordinatorEntity[IrsapHrdCoordinator], FanEntity):
    """Rappresenta una ventola dell'unità VMC IRSAP HRD."""

    _attr_has_entity_name = True
    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )

    def __init__(
        self,
        coordinator: IrsapHrdCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        speed_register: int,
        icon: str,
    ) -> None:
        """Inizializza l'entità Fan."""
        super().__init__(coordinator)
        self.entry = entry
        self.key = key
        self._attr_name = name
        self._speed_register = speed_register
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_fan_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=NAME,
            manufacturer="IRSAP / Dixell",
            model="HRD (iPro.GENIUS)",
            sw_version="FW 1.9",
        )

    @property
    def is_on(self) -> bool:
        """Indica se la macchina è accesa e la ventola è in funzione."""
        return bool(self.coordinator.data.get(REG_ON_OFF, 0))

    @property
    def speed_count(self) -> int:
        """Restituisce il numero totale di velocità disponibili (3 velocità)."""
        return int_states_in_range(SPEED_RANGE)

    @property
    def percentage(self) -> int | None:
        """Restituisce la percentuale di velocità corrente."""
        if not self.is_on:
            return 0
        current_speed = self.coordinator.data.get(self._speed_register, 1)
        return ranged_value_to_percentage(SPEED_RANGE, current_speed)

    async def async_set_percentage(self, percentage: int) -> None:
        """Imposta la velocità in percentuale (mappata su 1..3)."""
        if percentage == 0:
            # Se la percentuale è 0, spegnere la macchina non è desiderabile per una sola ventola,
            # ma impostiamo al minimo (velocità 1)
            await self.coordinator.async_write_register(self._speed_register, 1)
            return

        speed = math.ceil(percentage_to_ranged_value(SPEED_RANGE, percentage))
        speed = max(1, min(3, speed))
        await self.coordinator.async_write_register(self._speed_register, speed)

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Accende l'unità e/o imposta la velocità della ventola."""
        await self.coordinator.async_write_register(REG_ON_OFF, 1)
        if percentage is not None:
            await self.async_set_percentage(percentage)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Imposta la velocità al minimo."""
        await self.coordinator.async_write_register(self._speed_register, 1)
