"""Piattaforma Climate per IRSAP HRD VMC."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    NAME,
    REG_ESTATE_INVERNO,
    REG_ON_OFF,
    REG_SET_REG_ESTIVO,
    REG_SET_REG_INVERNALE,
    REG_TEMP_RIPRESA,
    REG_UMIDITA_RIPRESA,
    REG_VEL_ESPULSIONE,
    REG_VEL_RINNOVO,
)
from .coordinator import IrsapHrdCoordinator, to_signed_int16

_LOGGER = logging.getLogger(__name__)

FAN_MODE_LOW = FAN_LOW
FAN_MODE_MEDIUM = FAN_MEDIUM
FAN_MODE_HIGH = FAN_HIGH

FAN_MODE_MAP = {
    FAN_MODE_LOW: 1,
    FAN_MODE_MEDIUM: 2,
    FAN_MODE_HIGH: 3,
}

REV_FAN_MAP = {v: k for k, v in FAN_MODE_MAP.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configura l'entità Climate IRSAP HRD VMC."""
    coordinator: IrsapHrdCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([IrsapHrdClimate(coordinator, entry)])


class IrsapHrdClimate(CoordinatorEntity[IrsapHrdCoordinator], ClimateEntity):
    """Rappresentazione del climatizzatore/VMC IRSAP HRD."""

    _attr_has_entity_name = True
    _attr_translation_key = "vmc_climate"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 0.5
    _attr_min_temp = 10.0
    _attr_max_temp = 32.0
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.COOL]
    _attr_fan_modes = [FAN_MODE_LOW, FAN_MODE_MEDIUM, FAN_MODE_HIGH]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.FAN_MODE
    )

    def __init__(self, coordinator: IrsapHrdCoordinator, entry: ConfigEntry) -> None:
        """Inizializza l'entità Climate."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_climate"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=NAME,
            manufacturer="IRSAP / Dixell",
            model="HRD (iPro.GENIUS)",
            sw_version=coordinator.version,
        )

    @property
    def current_temperature(self) -> float | None:
        """Restituisce la temperatura attuale rilevata dalla sonda di ripresa ambiente."""
        raw = self.coordinator.data.get(REG_TEMP_RIPRESA)
        val = to_signed_int16(raw)
        return val / 10.0 if val is not None else None

    @property
    def current_humidity(self) -> float | None:
        """Restituisce l'umidità attuale rilevata dalla sonda di ripresa ambiente."""
        return self.coordinator.data.get(REG_UMIDITA_RIPRESA)

    @property
    def target_temperature(self) -> float | None:
        """Restituisce la temperatura target in base alla modalità attiva (Estate o Inverno)."""
        estate = self.coordinator.data.get(REG_ESTATE_INVERNO, 0)
        reg = REG_SET_REG_ESTIVO if estate == 1 else REG_SET_REG_INVERNALE
        raw = self.coordinator.data.get(reg)
        val = to_signed_int16(raw)
        return val / 10.0 if val is not None else None

    @property
    def hvac_mode(self) -> HVACMode:
        """Restituisce lo stato HVAC corrente."""
        on_off = self.coordinator.data.get(REG_ON_OFF, 0)
        if on_off == 0:
            return HVACMode.OFF
        estate = self.coordinator.data.get(REG_ESTATE_INVERNO, 0)
        return HVACMode.COOL if estate == 1 else HVACMode.HEAT

    @property
    def hvac_action(self) -> HVACAction | None:
        """Restituisce l'azione corrente della macchina."""
        on_off = self.coordinator.data.get(REG_ON_OFF, 0)
        if on_off == 0:
            return HVACAction.OFF
        estate = self.coordinator.data.get(REG_ESTATE_INVERNO, 0)
        return HVACAction.COOLING if estate == 1 else HVACAction.HEATING

    @property
    def fan_mode(self) -> str | None:
        """Restituisce la velocità corrente del ventilatore di rinnovo."""
        vel = self.coordinator.data.get(REG_VEL_RINNOVO, 1)
        return REV_FAN_MAP.get(vel, FAN_MODE_LOW)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Imposta la nuova temperatura desiderata."""
        temp = kwargs.get("temperature")
        if temp is None:
            return

        target_decimi = int(round(temp * 10))
        estate = self.coordinator.data.get(REG_ESTATE_INVERNO, 0)
        reg = REG_SET_REG_ESTIVO if estate == 1 else REG_SET_REG_INVERNALE

        await self.coordinator.async_write_register(reg, target_decimi)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Imposta la modalità operativa HVAC."""
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.async_write_register(REG_ON_OFF, 0)
            return

        # Accende la macchina
        await self.coordinator.async_write_register(REG_ON_OFF, 1)

        if hvac_mode == HVACMode.COOL:
            await self.coordinator.async_write_register(REG_ESTATE_INVERNO, 1)
        elif hvac_mode == HVACMode.HEAT:
            await self.coordinator.async_write_register(REG_ESTATE_INVERNO, 0)

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Imposta la velocità delle ventole."""
        val = FAN_MODE_MAP.get(fan_mode, 1)
        # Imposta contemporaneamente la velocità di rinnovo e di espulsione
        await self.coordinator.async_write_register(REG_VEL_RINNOVO, val)
        await self.coordinator.async_write_register(REG_VEL_ESPULSIONE, val)

    async def async_turn_on(self) -> None:
        """Accende l'unità VMC."""
        await self.coordinator.async_write_register(REG_ON_OFF, 1)

    async def async_turn_off(self) -> None:
        """Spegne l'unità VMC."""
        await self.coordinator.async_write_register(REG_ON_OFF, 0)
