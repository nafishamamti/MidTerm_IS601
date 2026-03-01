from decimal import Decimal
import logging

from app.calculator import Calculator
from app.commands import CalculateCommand, CommandQueue
from app.exceptions import OperationError, ValidationError
from app.help_menu import (
    BaseHelpMenu,
    OperationsHelpDecorator,
    SystemCommandsHelpDecorator,
)
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory
from app.output_style import OutputFormatter


def calculator_repl():
    """
    Command-line interface for the calculator.

    Implements a Read-Eval-Print Loop (REPL) that continuously prompts the user
    for commands, processes arithmetic operations, and manages calculation history.
    """
    try:
        # Initialize the Calculator instance
        calc = Calculator()
        formatter = OutputFormatter()

        # Register observers for logging and auto-saving history
        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))
        command_queue = CommandQueue()

        print(formatter.format("Calculator started. Type 'help' for commands.", "info"))

        while True:
            try:
                # Prompt the user for a command
                command = input("\nEnter command: ").lower().strip()
                operation_commands = OperationFactory.available_operations()
                operation_command_set = set(operation_commands)

                if command == 'help':
                    # Build help dynamically from currently registered operations.
                    help_menu = SystemCommandsHelpDecorator(
                        OperationsHelpDecorator(BaseHelpMenu(), operation_commands)
                    )
                    print("\nAvailable commands:")
                    for line in help_menu.render():
                        print(formatter.format(line, "info"))
                    continue

                if command == 'exit':
                    # Attempt to save history before exiting
                    try:
                        calc.save_history()
                        print(formatter.format("History saved successfully.", "success"))
                    except Exception as e:
                        print(formatter.format(f"Warning: Could not save history: {e}", "warning"))
                    print(formatter.format("Goodbye!", "info"))
                    break

                if command == 'history':
                    # Display calculation history
                    history = calc.show_history()
                    if not history:
                        print(formatter.format("No calculations in history", "warning"))
                    else:
                        print(formatter.format("\nCalculation History:", "info"))
                        for i, entry in enumerate(history, 1):
                            print(formatter.format(f"{i}. {entry}", "info"))
                    continue

                if command == 'clear':
                    # Clear calculation history
                    calc.clear_history()
                    print(formatter.format("History cleared", "success"))
                    continue

                if command == 'undo':
                    # Undo the last calculation
                    if calc.undo():
                        print(formatter.format("Operation undone", "success"))
                    else:
                        print(formatter.format("Nothing to undo", "warning"))
                    continue

                if command == 'redo':
                    # Redo the last undone calculation
                    if calc.redo():
                        print(formatter.format("Operation redone", "success"))
                    else:
                        print(formatter.format("Nothing to redo", "warning"))
                    continue

                if command == 'save':
                    # Save calculation history to file
                    try:
                        calc.save_history()
                        print(formatter.format("History saved successfully", "success"))
                    except Exception as e:
                        print(formatter.format(f"Error saving history: {e}", "error"))
                    continue

                if command == 'load':
                    # Load calculation history from file
                    try:
                        calc.load_history()
                        print(formatter.format("History loaded successfully", "success"))
                    except Exception as e:
                        print(formatter.format(f"Error loading history: {e}", "error"))
                    continue

                if command == 'queue':
                    try:
                        print(formatter.format("\nQueue an operation (or 'cancel' to abort):", "prompt"))
                        queued_operation_name = input("Operation: ").lower().strip()
                        if queued_operation_name == 'cancel':
                            print(formatter.format("Operation cancelled", "warning"))
                            continue
                        if queued_operation_name not in operation_command_set:
                            print(formatter.format(
                                f"Unknown operation: '{queued_operation_name}'. Use 'help' to view available operations.",
                                "warning"
                            ))
                            continue

                        a = input("First number: ")
                        if a.lower() == 'cancel':
                            print(formatter.format("Operation cancelled", "warning"))
                            continue
                        b = input("Second number: ")
                        if b.lower() == 'cancel':
                            print(formatter.format("Operation cancelled", "warning"))
                            continue

                        command_queue.enqueue(
                            CalculateCommand(
                                calculator=calc,
                                operation_name=queued_operation_name,
                                operand1=a,
                                operand2=b,
                                operation_factory=OperationFactory,
                            )
                        )
                        print(formatter.format(f"Operation queued. Queue size: {command_queue.size()}", "success"))
                    except Exception as e:
                        print(formatter.format(f"Error queueing operation: {e}", "error"))
                    continue

                if command == 'run_queue':
                    try:
                        if command_queue.size() == 0:
                            print(formatter.format("No queued operations to run", "warning"))
                            continue
                        results = command_queue.execute_all()
                        for i, result in enumerate(results, 1):
                            if isinstance(result, Decimal):
                                result = result.normalize()
                            print(formatter.format(f"Queued Result {i}: {result}", "success"))
                    except (ValidationError, OperationError) as e:
                        print(formatter.format(f"Error: {e}", "error"))
                    except Exception as e:
                        print(formatter.format(f"Unexpected error: {e}", "error"))
                    continue

                if command in operation_command_set:
                    # Perform the specified arithmetic operation
                    try:
                        print(formatter.format("\nEnter numbers (or 'cancel' to abort):", "prompt"))
                        a = input("First number: ")
                        if a.lower() == 'cancel':
                            print(formatter.format("Operation cancelled", "warning"))
                            continue
                        b = input("Second number: ")
                        if b.lower() == 'cancel':
                            print(formatter.format("Operation cancelled", "warning"))
                            continue

                        # Execute calculation via Command pattern.
                        result = CalculateCommand(
                            calculator=calc,
                            operation_name=command,
                            operand1=a,
                            operand2=b,
                            operation_factory=OperationFactory,
                        ).execute()

                        # Normalize the result if it's a Decimal
                        if isinstance(result, Decimal):
                            result = result.normalize()

                        print(formatter.format(f"\nResult: {result}", "success"))
                    except (ValidationError, OperationError) as e:
                        # Handle known exceptions related to validation or operation errors
                        print(formatter.format(f"Error: {e}", "error"))
                    except Exception as e:
                        # Handle any unexpected exceptions
                        print(formatter.format(f"Unexpected error: {e}", "error"))
                    continue

                # Handle unknown commands
                print(formatter.format(
                    f"Unknown command: '{command}'. Type 'help' for available commands.",
                    "warning"
                ))

            except KeyboardInterrupt:
                # Handle Ctrl+C interruption gracefully
                print(formatter.format("\nOperation cancelled", "warning"))
                continue
            except EOFError:
                # Handle end-of-file (e.g., Ctrl+D) gracefully
                print(formatter.format("\nInput terminated. Exiting...", "info"))
                break
            except Exception as e:
                # Handle any other unexpected exceptions
                print(formatter.format(f"Error: {e}", "error"))
                continue

    except Exception as e:
        # Handle fatal errors during initialization
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error in calculator REPL: {e}")
        raise
