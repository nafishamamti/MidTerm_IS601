from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from app.calculation import Calculation
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.calculator_repl import calculator_repl
from app.exceptions import OperationError, ValidationError
from app.operations import OperationFactory


@pytest.fixture
def calc_with_tmp_config(tmp_path):
    return Calculator(CalculatorConfig(base_dir=tmp_path))


def test_calculation_wraps_arithmetic_error():
    with pytest.raises(OperationError, match="Calculation failed"):
        Calculation(
            operation="Root",
            operand1=Decimal("4"),
            operand2=Decimal("1e-1000000"),
        )


def test_calculation_str_repr_and_eq_notimplemented():
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))
    assert str(calc) == "Addition(2, 3) = 5"
    assert "Calculation(operation='Addition'" in repr(calc)
    assert Calculation.__eq__(calc, object()) is NotImplemented


def test_memento_to_dict_and_from_dict_roundtrip():
    history = [Calculation("Addition", Decimal("2"), Decimal("3"))]
    memento = CalculatorMemento(history=history)
    data = memento.to_dict()
    restored = CalculatorMemento.from_dict(data)
    assert len(restored.history) == 1
    assert restored.history[0] == history[0]


def test_calculator_init_logs_warning_when_history_load_fails(tmp_path):
    config = CalculatorConfig(base_dir=tmp_path)
    with patch("app.calculator.Calculator.load_history", side_effect=Exception("boom")), \
         patch("app.calculator.logging.warning") as warn_mock:
        Calculator(config=config)
    assert any("Could not load existing history" in str(call) for call in warn_mock.call_args_list)


def test_setup_logging_re_raises_and_prints_error(tmp_path):
    config = CalculatorConfig(base_dir=tmp_path)
    with patch("app.calculator.logging.basicConfig", side_effect=Exception("logfail")), \
         patch("builtins.print") as print_mock, \
         pytest.raises(Exception, match="logfail"):
        Calculator(config=config)
    print_mock.assert_any_call("Error setting up logging: logfail")


def test_perform_operation_handles_unexpected_exception(calc_with_tmp_config):
    strategy = Mock()
    strategy.execute.side_effect = RuntimeError("explode")
    calc_with_tmp_config.set_operation(strategy)
    with pytest.raises(OperationError, match="Operation failed: explode"):
        calc_with_tmp_config.perform_operation(1, 2)


def test_perform_operation_trims_history_at_max_size(tmp_path):
    calc = Calculator(CalculatorConfig(base_dir=tmp_path, max_history_size=1))
    calc.set_operation(OperationFactory.create_operation("add"))
    calc.perform_operation(1, 2)
    calc.perform_operation(3, 4)
    assert len(calc.history) == 1
    assert calc.history[0].operand1 == Decimal("3")


def test_save_history_empty_and_exception_path(calc_with_tmp_config):
    calc_with_tmp_config.save_history()
    assert calc_with_tmp_config.config.history_file.exists()
    with patch("app.calculator.pd.DataFrame.to_csv", side_effect=Exception("csv-fail")):
        with pytest.raises(OperationError, match="Failed to save history: csv-fail"):
            calc_with_tmp_config.save_history()


def test_load_history_empty_and_exception_path(calc_with_tmp_config):
    with patch.object(Path, "exists", return_value=True), \
         patch("app.calculator.pd.read_csv", return_value=pd.DataFrame()):
        calc_with_tmp_config.load_history()

    with patch.object(Path, "exists", return_value=True), \
         patch("app.calculator.pd.read_csv", side_effect=Exception("read-fail")):
        with pytest.raises(OperationError, match="Failed to load history: read-fail"):
            calc_with_tmp_config.load_history()


def test_history_dataframe_show_history_and_empty_undo_redo(calc_with_tmp_config):
    assert calc_with_tmp_config.undo() is False
    assert calc_with_tmp_config.redo() is False

    calc_with_tmp_config.set_operation(OperationFactory.create_operation("add"))
    calc_with_tmp_config.perform_operation(2, 3)

    df = calc_with_tmp_config.get_history_dataframe()
    assert list(df.columns) == ["operation", "operand1", "operand2", "result", "timestamp"]
    assert df.iloc[0]["operation"] == "Addition"
    assert calc_with_tmp_config.show_history() == ["Addition(2, 3) = 5"]


def test_repl_history_clear_undo_redo_save_load_unknown_and_exit():
    mock_calc = Mock()
    mock_calc.show_history.side_effect = [[], ["Addition(2, 3) = 5"]]
    mock_calc.undo.side_effect = [True, False]
    mock_calc.redo.side_effect = [True, False]

    with patch("app.calculator_repl.Calculator", return_value=mock_calc), \
         patch(
             "builtins.input",
             side_effect=[
                 "history",
                 "history",
                 "clear",
                 "undo",
                 "undo",
                 "redo",
                 "redo",
                 "save",
                 "load",
                 "wat",
                 "exit",
             ],
         ), \
         patch("builtins.print") as print_mock:
        calculator_repl()

    print_mock.assert_any_call("No calculations in history")
    print_mock.assert_any_call("\nCalculation History:")
    print_mock.assert_any_call("History cleared")
    print_mock.assert_any_call("Operation undone")
    print_mock.assert_any_call("Nothing to undo")
    print_mock.assert_any_call("Operation redone")
    print_mock.assert_any_call("Nothing to redo")
    print_mock.assert_any_call("History saved successfully")
    print_mock.assert_any_call("History loaded successfully")
    print_mock.assert_any_call("Unknown command: 'wat'. Type 'help' for available commands.")
    print_mock.assert_any_call("Goodbye!")


def test_repl_exit_save_error_branch():
    mock_calc = Mock()
    mock_calc.save_history.side_effect = Exception("disk full")
    with patch("app.calculator_repl.Calculator", return_value=mock_calc), \
         patch("builtins.input", side_effect=["exit"]), \
         patch("builtins.print") as print_mock:
        calculator_repl()
    print_mock.assert_any_call("Warning: Could not save history: disk full")


def test_repl_save_and_load_command_error_branches():
    mock_calc = Mock()
    mock_calc.save_history.side_effect = Exception("save-err")
    mock_calc.load_history.side_effect = Exception("load-err")
    with patch("app.calculator_repl.Calculator", return_value=mock_calc), \
         patch("builtins.input", side_effect=["save", "load", "exit"]), \
         patch("builtins.print") as print_mock:
        calculator_repl()
    print_mock.assert_any_call("Error saving history: save-err")
    print_mock.assert_any_call("Error loading history: load-err")


def test_repl_add_cancel_and_error_branches():
    mock_calc = Mock()
    mock_calc.perform_operation.side_effect = [
        ValidationError("bad input"),
        Exception("boom"),
    ]
    with patch("app.calculator_repl.Calculator", return_value=mock_calc), \
         patch("app.calculator_repl.OperationFactory.create_operation", return_value=Mock()), \
         patch(
             "builtins.input",
             side_effect=[
                 "add", "cancel",
                 "add", "2", "cancel",
                 "add", "2", "3",
                 "add", "4", "5",
                 "exit",
             ],
         ), \
         patch("builtins.print") as print_mock:
        calculator_repl()
    print_mock.assert_any_call("Operation cancelled")
    print_mock.assert_any_call("Error: bad input")
    print_mock.assert_any_call("Unexpected error: boom")


def test_repl_keyboardinterrupt_eof_and_generic_input_exception():
    mock_calc = Mock()
    with patch("app.calculator_repl.Calculator", return_value=mock_calc), \
         patch("builtins.input", side_effect=[KeyboardInterrupt(), Exception("oops"), "exit"]), \
         patch("builtins.print") as print_mock:
        calculator_repl()
    print_mock.assert_any_call("\nOperation cancelled")
    print_mock.assert_any_call("Error: oops")

    with patch("app.calculator_repl.Calculator", return_value=mock_calc), \
         patch("builtins.input", side_effect=[EOFError()]), \
         patch("builtins.print") as print_mock:
        calculator_repl()
    print_mock.assert_any_call("\nInput terminated. Exiting...")


def test_repl_fatal_initialization_error():
    with patch("app.calculator_repl.Calculator", side_effect=Exception("init failed")), \
         patch("app.calculator_repl.logging.error") as log_error_mock, \
         patch("builtins.print") as print_mock:
        with pytest.raises(Exception, match="init failed"):
            calculator_repl()
    print_mock.assert_any_call("Fatal error: init failed")
    log_error_mock.assert_called_once()
