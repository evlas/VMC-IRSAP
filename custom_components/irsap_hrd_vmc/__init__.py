"""Inizializzazione del componente IRSAP HRD VMC per Home Assistant."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from .const import DOMAIN, PLATFORMS
from .coordinator import IrsapHrdCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configura l'integrazione IRSAP HRD VMC da una voce di configurazione."""
    hass.data.setdefault(DOMAIN, {})

    integration_version: str | None = None
    try:
        integration = await async_get_integration(hass, DOMAIN)
        if integration.version is not None:
            integration_version = str(integration.version)
    except Exception:
        pass

    coordinator = IrsapHrdCoordinator(
        hass,
        {**entry.data, **entry.options},
        version=integration_version,
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Rimuove una voce di configurazione."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: IrsapHrdCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_close()

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Ricarica la configurazione quando le opzioni vengono modificate."""
    await hass.config_entries.async_reload(entry.entry_id)
