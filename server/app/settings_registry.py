from typing import Dict, Type
import logging
from server.app.settings_observable import Observable

logger = logging.getLogger(__name__)


class SettingsRegistry:
    _settings_classes: Dict[str, Type[Observable]] = {}

    @classmethod
    def register(cls, key: str, settings_class: Type[Observable]):
        """Register a settings class with a key"""
        cls._settings_classes[key] = settings_class
        logger.info("Registered settings class for key: %s", key)

    @classmethod
    def create_settings(cls, parent: Observable) -> Dict[str, Observable]:
        """Create instances of all registered settings"""
        return {
            key: settings_class(parent) 
            for key, settings_class in cls._settings_classes.items()
        }