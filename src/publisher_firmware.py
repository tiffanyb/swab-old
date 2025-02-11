from __future__ import annotations

from itertools import repeat
from pathlib import Path
from pprint import pprint
from logging import DEBUG, NullHandler, basicConfig, getLogger

import click
import zmq

import automaton
import messages
import rover


class PublisherError(Exception):
    pass


def run(world: str, frequency: int, msg: messages.Start) -> list[messages.Step]:
    
    logger = getLogger("publisher")
    logger.addHandler(NullHandler())

    # TODO: I don't care about frequency and msg for now
    # cmds = iter(msg.commands)
    
    # vehicle = rover.remove(world)
    # print("removing the rover")
    vehicle = rover.spawn(world, magnet=msg.magnet)
    print("spawning the rover")

    # after spawning the rover, start to run the firmware simulation, which will post message to the rover.

    # the vehicle will listen to see if there is a stop command sending from the firmware, and then just stop.


    # controller = automaton.Automaton(vehicle)
    # controller = firmware.Firmware()
    # scheduler = sched.BlockingScheduler()
    # history: list[messages.Step] = []

    # def update():
    #     logger.debug("Running controller update")
    #     history.append(
    #         messages.Step(
    #             time=vehicle.clock,
    #             position=vehicle.position,
    #             heading=vehicle.heading,
    #             roll=vehicle.roll,
    #             state=controller.state,
    #         )
    #     )

    #     if controller.is_terminal:
    #         logger.debug("Found terminal state. Shutting down scheduler.")
    #         scheduler.shutdown()
    #     else:
    #         last_state = controller.state
    #         controller.step(next(cmds))
    #         logger.debug(f"Stepping controller. Last state: {last_state} -> Current state: {controller.state}")

    # logger.debug("Creating controller scheduler job")
    # scheduler.add_job(update, "interval", seconds=1/frequency)

    # logger.debug("Starting scheduler")
    # scheduler.start()

    # return history
    # TODO: right now we just return an empty history, since we don't want to involve psi-taliro for now.
    return []


@click.command()
@click.option("-w", "--world", default="default")
@click.option("-f", "--frequency", type=int, default=1)
@click.option("-s", "--socket", "socket_path", type=click.Path(exists=True, dir_okay=False, writable=True, path_type=Path), default=None)
@click.option("-v", "--verbose", is_flag=True)
def publisher(world: str, frequency: int, socket_path: Path | None, verbose: bool):
    logger = getLogger("publisher")
    logger.addHandler(NullHandler())

    if verbose:
        basicConfig(level=DEBUG)

    if socket_path is None:
        logger.debug("No socket provided, starting controller using defaults.")

        msg = messages.Start(commands=repeat(None), magnet=None)
        history = run(world, frequency, msg)

        # pprint(history)
    else:

        with zmq.Context() as ctx:
            with ctx.socket(zmq.REP) as sock:
                with sock.connect(str(socket_path)):
                    logger.debug("Listening for start message.")
                    msg = sock.recv_pyobj()

                    if not isinstance(msg, messages.Start):
                        sock.send_pyobj(PublisherError(f"Unexpected start message type {type(msg)}"))

                    logger.debug("Start message received. Running simulation.")
                    history = run(world, frequency, msg)
                    sock.send_pyobj(messages.Result(history))


if __name__ == "__main__":
    publisher()
