import trio

from .application import run


async def test_application():
    '''Tests if application launches without crashing'''

    with trio.move_on_after(5):
        await run()
