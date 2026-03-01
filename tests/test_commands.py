from decimal import Decimal
from unittest.mock import Mock

from app.commands import CalculateCommand, Command, CommandQueue


def test_abstract_command_default_body():
    class TestCommand(Command):
        def execute(self):
            return super().execute()

    assert TestCommand().execute() is None


def test_calculate_command_executes_with_factory_and_calculator():
    calculator = Mock()
    calculator.perform_operation.return_value = Decimal("5")
    operation_instance = Mock()
    operation_factory = Mock()
    operation_factory.create_operation.return_value = operation_instance

    command = CalculateCommand(
        calculator=calculator,
        operation_name="add",
        operand1="2",
        operand2="3",
        operation_factory=operation_factory,
    )

    result = command.execute()

    operation_factory.create_operation.assert_called_once_with("add")
    calculator.set_operation.assert_called_once_with(operation_instance)
    calculator.perform_operation.assert_called_once_with("2", "3")
    assert result == Decimal("5")


def test_command_queue_execute_next_on_empty_returns_none():
    queue = CommandQueue()
    assert queue.execute_next() is None


def test_command_queue_enqueue_execute_next_and_size():
    queue = CommandQueue()
    command = Mock()
    command.execute.return_value = 42

    queue.enqueue(command)
    assert queue.size() == 1
    assert queue.execute_next() == 42
    assert queue.size() == 0


def test_command_queue_execute_all_and_clear():
    queue = CommandQueue()
    c1 = Mock()
    c2 = Mock()
    c1.execute.return_value = "r1"
    c2.execute.return_value = "r2"
    queue.enqueue(c1)
    queue.enqueue(c2)

    assert queue.execute_all() == ["r1", "r2"]
    assert queue.size() == 0

    queue.enqueue(c1)
    queue.clear()
    assert queue.size() == 0
