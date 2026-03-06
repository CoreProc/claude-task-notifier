from unittest.mock import patch, MagicMock
from src.notifier.toast import show_notification


@patch("src.notifier.toast.ToastNotifier")
def test_show_notification_calls_toast(mock_class):
    mock_instance = MagicMock()
    mock_class.return_value = mock_instance

    show_notification("Task X finished")

    mock_instance.show_toast.assert_called_once()
    args, kwargs = mock_instance.show_toast.call_args
    assert kwargs["title"] == "Claude Code"
    assert "Task X finished" in kwargs["msg"]
    assert kwargs["duration"] == 10
    assert kwargs["threaded"] is True
