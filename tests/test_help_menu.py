from app.help_menu import (
    HelpMenuComponent,
    BaseHelpMenu,
    OperationsHelpDecorator,
    SystemCommandsHelpDecorator,
)


def test_help_menu_component_default_abstract_body():
    class TestComponent(HelpMenuComponent):
        def render(self):
            return super().render()

    assert TestComponent().render() is None


def test_help_menu_decorator_composition():
    menu = SystemCommandsHelpDecorator(
        OperationsHelpDecorator(BaseHelpMenu(), ["add", "multiply", "root"])
    )

    lines = menu.render()

    assert lines[0] == "  add, multiply, root - Perform calculations"
    assert "  history - Show calculation history" in lines
    assert "  exit - Exit the calculator" in lines
