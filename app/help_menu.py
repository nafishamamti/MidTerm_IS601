from abc import ABC, abstractmethod
from typing import Iterable, List


class HelpMenuComponent(ABC):
    """Component interface for the help menu."""

    @abstractmethod
    def render(self) -> List[str]:
        """Return help menu lines."""
        pass


class BaseHelpMenu(HelpMenuComponent):
    """Concrete base component for help menu."""

    def render(self) -> List[str]:
        return []


class HelpMenuDecorator(HelpMenuComponent):
    """Base decorator that wraps another help menu component."""

    def __init__(self, component: HelpMenuComponent):
        self._component = component

    def render(self) -> List[str]:
        return self._component.render()


class OperationsHelpDecorator(HelpMenuDecorator):
    """Decorator that adds operation commands dynamically."""

    def __init__(self, component: HelpMenuComponent, operations: Iterable[str]):
        super().__init__(component)
        self._operations = list(operations)

    def render(self) -> List[str]:
        lines = super().render()
        operations_line = ", ".join(self._operations)
        lines.append(f"  {operations_line} - Perform calculations")
        return lines


class SystemCommandsHelpDecorator(HelpMenuDecorator):
    """Decorator that adds non-operation REPL commands."""

    def render(self) -> List[str]:
        lines = super().render()
        lines.extend([
            "  history - Show calculation history",
            "  clear - Clear calculation history",
            "  undo - Undo the last calculation",
            "  redo - Redo the last undone calculation",
            "  save - Save calculation history to file",
            "  load - Load calculation history from file",
            "  queue - Add an operation to the execution queue",
            "  run_queue - Execute all queued operations",
            "  exit - Exit the calculator",
        ])
        return lines
