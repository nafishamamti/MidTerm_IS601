from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from decimal import Decimal
from typing import Deque, Optional, Protocol, Union

from app.calculator import Calculator, Number
from app.operations import OperationFactory


class OperationFactoryProtocol(Protocol):
    """Protocol for operation factory implementations used by commands."""

    @staticmethod
    def create_operation(operation_type: str):
        """Create an operation instance."""


class Command(ABC):
    """Abstract command interface."""

    @abstractmethod
    def execute(self):
        """Execute the encapsulated request."""
        pass


@dataclass
class CalculateCommand(Command):
    """Command that executes a calculator operation with parameterized operands."""

    calculator: Calculator
    operation_name: str
    operand1: Union[str, Number]
    operand2: Union[str, Number]
    operation_factory: OperationFactoryProtocol = OperationFactory

    def execute(self) -> Union[int, float, Decimal, str]:
        operation = self.operation_factory.create_operation(self.operation_name)
        self.calculator.set_operation(operation)
        return self.calculator.perform_operation(self.operand1, self.operand2)


class CommandQueue:
    """FIFO queue for command objects."""

    def __init__(self):
        self._queue: Deque[Command] = deque()

    def enqueue(self, command: Command) -> None:
        """Add a command to the queue."""
        self._queue.append(command)

    def execute_next(self):
        """Execute and remove the next command, if any."""
        if not self._queue:
            return None
        return self._queue.popleft().execute()

    def execute_all(self) -> list:
        """Execute all queued commands and return their results in order."""
        results = []
        while self._queue:
            results.append(self.execute_next())
        return results

    def size(self) -> int:
        """Return number of queued commands."""
        return len(self._queue)

    def clear(self) -> None:
        """Clear all queued commands."""
        self._queue.clear()
