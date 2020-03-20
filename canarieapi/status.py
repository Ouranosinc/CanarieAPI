
class Status:
    ok = 'ok'
    bad = 'bad'
    down = 'down'

    def __init__(self):
        pass

    @staticmethod
    def pretty_msg(status):
        if status == Status.ok:
            return 'Ok'
        elif status == Status.bad:
            return 'Up but returning unexpected response'
        elif status == Status.down:
            return 'Down'
        else:
            return 'Unknown status'
