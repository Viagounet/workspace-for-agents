class Action:
    def __init__(self) -> None:
        pass


class SendEmail(Action):
    def __init__(self, sender: str, receiver: str, content: str) -> None:
        super().__init__()
        self.sender = sender
        self.receiver = receiver
        self.content = content


class Wait(Action):
    def __init__(self) -> None:
        super().__init__()
