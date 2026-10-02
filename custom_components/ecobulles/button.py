"""Reset control for Ecobulles bottle usage estimates."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .sensor import EcobullesCoordinator

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the CO2 bottle estimate reset button."""
    async_add_entities(
        [
            ResetCO2BottleUsageButton(coordinator, eco_ref)
            for eco_ref, coordinator in entry.runtime_data.coordinators.items()
        ]
    )


class ResetCO2BottleUsageButton(
    CoordinatorEntity[EcobullesCoordinator], ButtonEntity
):
    """Reset the estimated usage after installing a new CO2 bottle."""

    _attr_has_entity_name = True
    _attr_translation_key = "reset_co2_bottle_usage"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: EcobullesCoordinator, eco_ref: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{eco_ref}_reset_co2_bottle_usage"
        self._attr_device_info = {"identifiers": {(DOMAIN, eco_ref)}}

    async def async_press(self) -> None:
        """Reset usage to zero for the newly installed bottle."""
        await self.coordinator.async_reset_co2_usage()
