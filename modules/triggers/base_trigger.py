import abc

from datetime import datetime
from typing import Callable, Any


class BaseTrigger(abc.ABC):
    def __init__(self, workflow: Callable[[], Any]):
        self.workflow = workflow
        self._active = False

    @abc.abstractmethod
    def check_condition(self) -> bool:
        """Check if trigger condition is met"""
        raise NotImplementedError

    @abc.abstractmethod
    def start(self):
        """Start monitoring for trigger events"""
        raise NotImplementedError

    def stop(self):
        """Stop the trigger"""
        self._active = False

    def execute_workflow(self):
        """Execute the associated workflow"""
        return self.workflow()