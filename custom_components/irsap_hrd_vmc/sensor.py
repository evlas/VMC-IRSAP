"""Piattaforma Sensori per IRSAP HRD VMC."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    NAME,
    REG_AI_BASE,
    REG_AO_BASE,
    REG_QUALITA_ARIA,
    REG_RTC_ANNO,
    REG_RTC_GIORNO,
    REG_RTC_MESE,
    REG_RTC_MINUTI,
    REG_RTC_ORA,
    REG_TEMP_ARIA_ESTERNA,
    REG_TEMP_ESPULSIONE,
    REG_TEMP_IMMISSIONE,
    REG_TEMP_RIPRESA,
    REG_UMIDITA_RIPRESA,
)
from .coordinator import IrsapHrdCoordinator, to_signed_int16

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configura i sensori per IRSAP HRD VMC."""
    coordinator: IrsapHrdCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        # Sonde di temperatura
        IrsapHrdTempSensor(
            coordinator,
            entry,
            key="temp_ripresa",
            name="Temperatura Ripresa Ambiente",
            register=REG_TEMP_RIPRESA,
            icon="mdi:home-thermometer",
        ),
        IrsapHrdTempSensor(
            coordinator,
            entry,
            key="temp_immissione",
            name="Temperatura Immissione",
            register=REG_TEMP_IMMISSIONE,
            icon="mdi:weather-dust",
        ),
        IrsapHrdTempSensor(
            coordinator,
            entry,
            key="temp_espulsione",
            name="Temperatura Espulsione",
            register=REG_TEMP_ESPULSIONE,
            icon="mdi:weather-dust",
        ),
        IrsapHrdTempSensor(
            coordinator,
            entry,
            key="temp_esterna",
            name="Temperatura Aria Esterna",
            register=REG_TEMP_ARIA_ESTERNA,
            icon="mdi:thermometer-chevron-up",
        ),
        # Umidità
        IrsapHrdHumiditySensor(
            coordinator,
            entry,
            key="umidita_ripresa",
            name="Umidità Ripresa Ambiente",
            register=REG_UMIDITA_RIPRESA,
        ),
        # Qualità aria
        IrsapHrdAirQualitySensor(
            coordinator,
            entry,
            key="qualita_aria",
            name="Qualità Aria",
            register=REG_QUALITA_ARIA,
        ),
        # Efficienza recuperatore
        IrsapHrdEfficiencySensor(
            coordinator,
            entry,
        ),
        # Orologio RTC interno
        IrsapHrdRtcSensor(
            coordinator,
            entry,
        ),
    ]

    # Ingressi analogici AI01..AI06 (Diagnostici)
    for i in range(6):
        entities.append(
            IrsapHrdAnalogIoSensor(
                coordinator,
                entry,
                key=f"ai0{i+1}",
                name=f"Ingresso Analogico AI0{i+1}",
                register=REG_AI_BASE + i,
            )
        )

    # Uscite analogiche AO01..AO04 (Diagnostici)
    for i in range(4):
        entities.append(
            IrsapHrdAnalogIoSensor(
                coordinator,
                entry,
                key=f"ao0{i+1}",
                name=f"Uscita Analogica AO0{i+1}",
                register=REG_AO_BASE + i,
            )
        )

    async_add_entities(entities)


class IrsapHrdBaseSensor(CoordinatorEntity[IrsapHrdCoordinator], SensorEntity):
    """Classe base per i sensori IRSAP HRD."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: IrsapHrdCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
    ) -> None:
        """Inizializza il sensore base."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_translation_key = key
        self._attr_unique_id = f"{entry.entry_id}_sensor_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=NAME,
            manufacturer="IRSAP / Dixell",
            model="HRD (iPro.GENIUS)",
            sw_version=coordinator.version,
        )


class IrsapHrdTempSensor(IrsapHrdBaseSensor):
    """Sensore di temperatura con scala 0.1 °C e supporto a valori negativi."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(
        self,
        coordinator: IrsapHrdCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        register: int,
        icon: str | None = None,
    ) -> None:
        """Inizializza il sensore di temperatura."""
        super().__init__(coordinator, entry, key, name)
        self.register = register
        if icon:
            self._attr_icon = icon

    @property
    def native_value(self) -> float | None:
        """Restituisce il valore in °C."""
        raw = self.coordinator.data.get(self.register)
        val = to_signed_int16(raw)
        return round(val / 10.0, 1) if val is not None else None


class IrsapHrdHumiditySensor(IrsapHrdBaseSensor):
    """Sensore di umidità relativa."""

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:water-percent"

    def __init__(
        self,
        coordinator: IrsapHrdCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        register: int,
    ) -> None:
        """Inizializza il sensore di umidità."""
        super().__init__(coordinator, entry, key, name)
        self.register = register

    @property
    def native_value(self) -> int | None:
        """Restituisce l'umidità in %."""
        return self.coordinator.data.get(self.register)


class IrsapHrdAirQualitySensor(IrsapHrdBaseSensor):
    """Sensore per la qualità dell'aria."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:air-filter"

    def __init__(
        self,
        coordinator: IrsapHrdCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        register: int,
    ) -> None:
        """Inizializza il sensore qualità aria."""
        super().__init__(coordinator, entry, key, name)
        self.register = register

    @property
    def native_value(self) -> int | None:
        """Restituisce il valore numerico della qualità dell'aria."""
        return self.coordinator.data.get(self.register)


class IrsapHrdEfficiencySensor(IrsapHrdBaseSensor):
    """Sensore per l'efficienza termica del recuperatore (%)."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:percent-box"

    def __init__(
        self,
        coordinator: IrsapHrdCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Inizializza il sensore efficienza."""
        super().__init__(coordinator, entry, "efficienza_recupero", "Efficienza Recupero Termico")

    @property
    def native_value(self) -> float | None:
        """Calcola l'efficienza di recupero: (T_imm - T_est) / (T_rip - T_est) * 100."""
        t_imm_raw = to_signed_int16(self.coordinator.data.get(REG_TEMP_IMMISSIONE))
        t_rip_raw = to_signed_int16(self.coordinator.data.get(REG_TEMP_RIPRESA))
        t_est_raw = to_signed_int16(self.coordinator.data.get(REG_TEMP_ARIA_ESTERNA))

        if t_imm_raw is None or t_rip_raw is None or t_est_raw is None:
            return None

        delta_tot = t_rip_raw - t_est_raw
        if abs(delta_tot) < 5:  # Evita divisioni per zero o instabilità con differenze minime (< 0.5 °C)
            return None

        eff = ((t_imm_raw - t_est_raw) / delta_tot) * 100.0
        # Normalizza tra 0% e 100%
        return round(max(0.0, min(100.0, eff)), 1)


class IrsapHrdRtcSensor(IrsapHrdBaseSensor):
    """Sensore per la data e ora dell'orologio interno (RTC) del Dixell iPro."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:clock-outline"

    def __init__(
        self,
        coordinator: IrsapHrdCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Inizializza il sensore RTC."""
        super().__init__(coordinator, entry, "rtc_orologio", "Data e Ora Macchina (RTC)")

    @property
    def native_value(self) -> str | None:
        """Restituisce data e ora formattata YYYY-MM-DD HH:MM."""
        anno = self.coordinator.data.get(REG_RTC_ANNO)
        mese = self.coordinator.data.get(REG_RTC_MESE)
        giorno = self.coordinator.data.get(REG_RTC_GIORNO)
        ora = self.coordinator.data.get(REG_RTC_ORA)
        minuti = self.coordinator.data.get(REG_RTC_MINUTI)

        if None in (anno, mese, giorno, ora, minuti):
            return None

        # Se l'anno è su 2 cifre (es. 24), normalizza a 2024
        full_anno = anno + 2000 if anno < 100 else anno
        return f"{full_anno:04d}-{mese:02d}-{giorno:02d} {ora:02d}:{minuti:02d}"


class IrsapHrdAnalogIoSensor(IrsapHrdBaseSensor):
    """Sensore diagnostico per ingressi/uscite analogiche fisiche."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: IrsapHrdCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        register: int,
    ) -> None:
        """Inizializza il sensore analogico diagnostico."""
        super().__init__(coordinator, entry, key, name)
        self.register = register

    @property
    def native_value(self) -> int | None:
        """Restituisce il valore grezzo letto."""
        return self.coordinator.data.get(self.register)
