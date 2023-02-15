from canarieapi.status import Status


def test_status():
    assert "Ok" in Status.pretty_msg(Status.ok)
    assert "Up" in Status.pretty_msg(Status.bad)
    assert "Down" in Status.pretty_msg(Status.down)
    assert "Unknown" in Status.pretty_msg("random")  # type: ignore
