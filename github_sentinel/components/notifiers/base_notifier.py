from abc import ABC, abstractmethod

class BaseNotifier(ABC):
    """Abstract base class for all notifiers."""

    @abstractmethod
    def send(self, message: str):
        """
        Sends a message to the notification channel.
        
        Args:
            message (str): The content of the message to send.
        """
        pass
