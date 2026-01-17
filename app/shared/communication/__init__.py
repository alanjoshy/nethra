"""
Module communication pattern - Internal Service Bus/Facade.
Modules communicate through this interface to avoid tight coupling.
"""

from typing import Protocol, TypeVar, Optional, Any
from abc import ABC, abstractmethod

T = TypeVar("T")


class ModuleService(Protocol):
    """
    Protocol for module services that can be called by other modules.
    Each module should expose its public API through a service that implements this protocol.
    """
    pass


class InternalServiceBus:
    """
    Internal service bus for inter-module communication.
    Modules register their public services here, and other modules access them through this bus.
    """
    
    def __init__(self):
        self._services: dict[str, Any] = {}
    
    def register_service(self, module_name: str, service: Any) -> None:
        """
        Register a module's public service.
        
        Args:
            module_name: Name of the module (e.g., 'users', 'cases')
            service: The public service instance or class
        """
        self._services[module_name] = service
    
    def get_service(self, module_name: str) -> Any:
        """
        Get a module's public service.
        
        Args:
            module_name: Name of the module
            
        Returns:
            The registered service
            
        Raises:
            KeyError: If module is not registered
        """
        if module_name not in self._services:
            raise KeyError(f"Module '{module_name}' is not registered in the service bus")
        return self._services[module_name]
    
    def has_service(self, module_name: str) -> bool:
        """Check if a module service is registered."""
        return module_name in self._services


# Global service bus instance
_service_bus = InternalServiceBus()


def get_service_bus() -> InternalServiceBus:
    """Get the global service bus instance."""
    return _service_bus


__all__ = [
    "ModuleService",
    "InternalServiceBus",
    "get_service_bus",
]
