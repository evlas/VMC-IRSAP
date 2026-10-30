"""Piattaforma Number per setpoint e parametri regolabili di IRSAP HRD VMC."""

from __future__ import annotations

import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    NAME,
    REG_DIFF_REGOLAZIONE,
    REG_DIFF_UMIDITA,
    REG_FASCIA_ORA_START_1,
    REG_FASCIA_ORA_START_2,
    REG_FASCIA_ORA_START_3,
    REG_FASCIA_ORA_STOP_1,
    REG_FASCIA_ORA_STOP_2,
    REG_FASCIA_ORA_STOP_3,
    REG_SET_REG_ESTIVO,
    REG_SET_REG_INVERNALE,
    REG_SET_UMIDITA_ESTIVO,
    REG_SET_UMIDITA_INV,
    REG_VEL_ESPULSIONE,
    REG_VEL_RINNOVO,
    REG_VEL_RINNOVO_DEU,
)
from .coordinator import IrsapHrdCoordinator, to_signed_int16

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configura le entità Number per IRSAP HRD VMC."""
    coordinator: IrsapHrdCoordinator = hass.data[DOMAIN][entry.entry_id]

    numbers: list[NumberEntity] = [
        # Setpoint Temperature
        IrsapHrdScaledNumber(
            coordinator,
            entry,
            key="set_reg_estivo",
            name="Setpoint Temperatura Estivo",
            register=REG_SET_REG_ESTIVO,
            scale=0.1,
            min_value=15.0,
            max_value=32.0,
            step=0.5,
            unit=UnitOfTemperature.CELSIUS,
            device_class=NumberDeviceClass.TEMPERATURE,
            icon="mdi:weather-sunny",
        ),
        IrsapHrdScaledNumber(
            coordinator,
            entry,
            key="set_reg_invernale",
            name="Setpoint Temperatura Invernale",
            register=REG_SET_REG_INVERNALE,
            scale=0.1,
            min_value=15.0,
            max_value=32.0,
            step=0.5,
            unit=UnitOfTemperature.CELSIUS,
            device_class=NumberDeviceClass.TEMPERATURE,
            icon="mdi:snowflake",
        ),
        IrsapHrdScaledNumber(
            coordinator,
            entry,
            key="diff_regolazione",
            name="Differenziale Temperatura",
            register=REG_DIFF_REGOLAZIONE,
            scale=0.1,
            min_value=0.5,
            max_value=5.0,
            step=0.1,
            unit=UnitOfTemperature.CELSIUS,
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:delta",
        ),
        # Setpoint Umidità
        IrsapHrdDirectNumber(
            coordinator,
            entry,
            key="set_umidita_estivo",
            name="Setpoint Umidità Estivo",
            register=REG_SET_UMIDITA_ESTIVO,
            min_value=30,
            max_value=85,
            step=1,
            unit=PERCENTAGE,
            device_class=NumberDeviceClass.HUMIDITY,
            icon="mdi:water-percent",
        ),
        IrsapHrdDirectNumber(
            coordinator,
            entry,
            key="set_umidita_invernale",
            name="Setpoint Umidità Invernale",
            register=REG_SET_UMIDITA_INV,
            min_value=30,
            max_value=85,
            step=1,
            unit=PERCENTAGE,
            device_class=NumberDeviceClass.HUMIDITY,
            icon="mdi:water-percent",
        ),
        IrsapHrdDirectNumber(
            coordinator,
            entry,
            key="diff_umidita",
            name="Differenziale Umidità",
            register=REG_DIFF_UMIDITA,
            min_value=1,
            max_value=20,
            step=1,
            unit=PERCENTAGE,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:water-opacity",
        ),
        # Velocità Ventole (1..3)
        IrsapHrdDirectNumber(
            coordinator,
            entry,
            key="vel_rinnovo",
            name="Velocità Rinnovo (1-3)",
            register=REG_VEL_RINNOVO,
            min_value=1,
            max_value=3,
            step=1,
            icon="mdi:fan",
        ),
        IrsapHrdDirectNumber(
            coordinator,
            entry,
            key="vel_espulsione",
            name="Velocità Espulsione (1-3)",
            register=REG_VEL_ESPULSIONE,
            min_value=1,
            max_value=3,
            step=1,
            icon="mdi:fan-chevron-up",
        ),
        IrsapHrdDirectNumber(
            coordinator,
            entry,
            key="vel_rinnovo_deu",
            name="Velocità Rinnovo Deumidificazione (1-3)",
            register=REG_VEL_RINNOVO_DEU,
            min_value=1,
            max_value=3,
            step=1,
            icon="mdi:fan-auto",
        ),
        # Fasce Orarie (Orari inizio/fine 0..23)
        IrsapHrdDirectNumber(
            coordinator,
            entry,
            key="ora_start_fascia_1",
            name="Ora Inizio Fascia 1",
            register=REG_FASCIA_ORA_START_1,
            min_value=0,
            max_value=23,
            step=1,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:clock-start",
        ),
        IrsapHrdDirectNumber(
            coordinator,
            entry,
            key="ora_stop_fascia_1",
            name="Ora Fine Fascia 1",
            register=REG_FASCIA_ORA_STOP_1,
            min_value=0,
            max_value=23,
            step=1,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:clock-end",
        ),
        IrsapHrdDirectNumber(
            coordinator,
            entry,
            key="ora_start_fascia_2",
            name="Ora Inizio Fascia 2",
            register=REG_FASCIA_ORA_START_2,
            min_value=0,
            max_value=23,
            step=1,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:clock-start",
        ),
        IrsapHrdDirectNumber(
            coordinator,
            entry,
            key="ora_stop_fascia_2",
            name="Ora Fine Fascia 2",
            register=REG_FASCIA_ORA_STOP_2,
            min_value=0,
            max_value=23,
            step=1,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:clock-end",
        ),
        IrsapHrdDirectNumber(
            coordinator,
            entry,
            key="ora_start_fascia_3",
            name="Ora Inizio Fascia 3",
            register=REG_FASCIA_ORA_START_3,
            min_value=0,
            max_value=23,
            step=1,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:clock-start",
        ),
        IrsapHrdDirectNumber(
            coordinator,
            entry,
            key="ora_stop_fascia_3",
            name="Ora Fine Fascia 3",
            register=REG_FASCIA_ORA_STOP_3,
            min_value=0,
            max_value=23,
            step=1,
            entity_category=EntityCategory.CONFIG,
            icon="mdi:clock-end",
        ),
    ]

    async_add_entities(numbers)


class IrsapHrdBaseNumber(CoordinatorEntity[IrsapHrdCoordinator], NumberEntity):
    """Classe base per le entità Number di IRSAP HRD."""

    _attr_has_entity_name = True
    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        coordinator: IrsapHrdCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        register: int,
        icon: str | None = None,
        entity_category: EntityCategory | None = None,
    ) -> None:
        """Inizializza l'entità Number base."""
        super().__init__(coordinator)
        self.entry = entry
        self.register = register
        self._attr_translation_key = key
        if icon:
            self._attr_icon = icon
        if entity_category:
            self._attr_entity_category = entity_category
        self._attr_unique_id = f"{entry.entry_id}_num_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=NAME,
            manufacturer="IRSAP / Dixell",
            model="HRD (iPro.GENIUS)",
            sw_version=coordinator.version,
        )


class IrsapHrdScaledNumber(IrsapHrdBaseNumber):
    """Numero con fattore di scala (es. decimi di grado centigrado)."""

    def __init__(
        self,
        coordinator: IrsapHrdCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        register: int,
        scale: float,
        min_value: float,
        max_value: float,
        step: float,
        unit: str,
        device_class: NumberDeviceClass | None = None,
        icon: str | None = None,
        entity_category: EntityCategory | None = None,
    ) -> None:
        """Inizializza il numero in scala."""
        super().__init__(coordinator, entry, key, name, register, icon, entity_category)
        self.scale = scale
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = unit
        if device_class:
            self._attr_device_class = device_class

    @property
    def native_value(self) -> float | None:
        """Restituisce il valore in scala reale."""
        raw = self.coordinator.data.get(self.register)
        val = to_signed_int16(raw)
        return round(val * self.scale, 1) if val is not None else None

    async def async_set_native_value(self, value: float) -> None:
        """Converte il valore nel formato registro intero e lo invia via Modbus."""
        target_raw = int(round(value / self.scale))
        await self.coordinator.async_write_register(self.register, target_raw)


class IrsapHrdDirectNumber(IrsapHrdBaseNumber):
    """Numero con corrispondenza 1 a 1 senza fattore di scala."""

    def __init__(
        self,
        coordinator: IrsapHrdCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        register: int,
        min_value: float,
        max_value: float,
        step: float,
        unit: str | None = None,
        device_class: NumberDeviceClass | None = None,
        icon: str | None = None,
        entity_category: EntityCategory | None = None,
    ) -> None:
        """Inizializza il numero diretto."""
        super().__init__(coordinator, entry, key, name, register, icon, entity_category)
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        if unit:
            self._attr_native_unit_of_measurement = unit
        if device_class:
            self._attr_device_class = device_class

    @property
    def native_value(self) -> float | None:
        """Restituisce il valore diretto del registro."""
        return self.coordinator.data.get(self.register)

    async def async_set_native_value(self, value: float) -> None:
        """Scrive direttamente il valore intero nel registro Modbus."""
        await self.coordinator.async_write_register(self.register, int(value))
