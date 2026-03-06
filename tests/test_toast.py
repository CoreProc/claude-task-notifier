from unittest.mock import patch, MagicMock
from src.notifier.toast import show_notification


@patch("src.notifier.toast.Notification")
def test_show_notification_with_project(mock_class):
    mock_instance = MagicMock()
    mock_class.return_value = mock_instance

    show_notification("Task X finished", "my-app")

    mock_class.assert_called_once()
    kwargs = mock_class.call_args[1]
    assert kwargs["title"] == "Claude Code — my-app"
    assert "Task X finished" in kwargs["msg"]


@patch("src.notifier.toast.Notification")
def test_show_notification_without_project(mock_class):
    mock_instance = MagicMock()
    mock_class.return_value = mock_instance

    show_notification("Done")

    kwargs = mock_class.call_args[1]
    assert kwargs["title"] == "Claude Code"
