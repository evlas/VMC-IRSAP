"""Piattaforma Binary Sensor per IRSAP HRD VMC."""

from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME, REG_ALLARME_GENERALE, REG_DI_BASE, REG_RL_BASE
from .coordinator import IrsapHrdCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configura i sensori binari per IRSAP HRD VMC."""
    coordinator: IrsapHrdCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[BinarySensorEntity] = [
        # Allarme Generale Principale
        IrsapHrdAlarmBinarySensor(
            coordinator,
            entry,
        )
    ]

    # Ingressi digitali fisici DI01..DI08 (Diagnostica)
    for i in range(8):
        entities.append(
            IrsapHrdDiagnosticBinarySensor(
                coordinator,
                entry,
                key=f"di0{i+1}",
                name=f"Ingresso Digitale DI0{i+1}",
                register=REG_DI_BASE + i,
                icon="mdi:import",
            )
        )

    # Uscite relè fisiche RL01..RL08 (Diagnostica)
    for i in range(8):
        entities.append(
            IrsapHrdDiagnosticBinarySensor(
                coordinator,
                entry,
                key=f"rl0{i+1}",
                name=f"Stato Relè RL0{i+1}",
                register=REG_RL_BASE + i,
                icon="mdi:electric-switch",
            )
        )

    async_add_entities(entities)


class IrsapHrdAlarmBinarySensor(
    CoordinatorEntity[IrsapHrdCoordinator], BinarySensorEntity
):
    """Sensore per l'allarme generale della macchina."""

    _attr_has_entity_name = True
    _attr_translation_key = "allarme_generale"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self,
        coordinator: IrsapHrdCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Inizializza il sensore allarme."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_allarme_generale"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=NAME,
            manufacturer="IRSAP / Dixell",
            model="HRD (iPro.GENIUS)",
            sw_version=coordinator.version,
        )

    @property
    def is_on(self) -> bool | None:
        """Restituisce True se l'allarme è attivo."""
        val = self.coordinator.data.get(REG_ALLARME_GENERALE)
        return bool(val == 1) if val is not None else None


class IrsapHrdDiagnosticBinarySensor(
    CoordinatorEntity[IrsapHrdCoordinator], BinarySensorEntity
):
    """Sensore binario diagnostico per ingressi e relè fisici."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: IrsapHrdCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        register: int,
        icon: str,
    ) -> None:
        """Inizializza il sensore diagnostico."""
        super().__init__(coordinator)
        self.entry = entry
        self.register = register
        self._attr_translation_key = key
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_bin_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=NAME,
            manufacturer="IRSAP / Dixell",
            model="HRD (iPro.GENIUS)",
            sw_version=coordinator.version,
        )

    @property
    def is_on(self) -> bool | None:
        """Restituisce True se l'ingresso/relè è attivo (1)."""
        val = self.coordinator.data.get(self.register)
        return bool(val == 1) if val is not None else None
