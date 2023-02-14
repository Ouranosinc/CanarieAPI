
class Status:
    ok = "ok"
    bad = "bad"
    down = "down"

    def __init__(self):
        pass

    @staticmethod
    def pretty_msg(status: "Status") -> str:
        if status == Status.ok:
            return "Ok"
        if status == Status.bad:
            return "Up but returning unexpected response"
        if status == Status.down:
            return "Down"
        return "Unknown status"
