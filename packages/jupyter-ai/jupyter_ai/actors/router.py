from jupyter_ai.actors.base import ACTOR_TYPE, COMMANDS, Logger, BaseActor
from jupyter_ai.models import ClearMessage

import ray
from ray.util.queue import Queue


@ray.remote
class Router(BaseActor):
    def __init__(self, reply_queue: Queue, log: Logger):
        """Routes messages to the correct actor.
        
        To register new actors, add the actor type in the `ACTOR_TYPE` enum and 
        add a corresponding command in the `COMMANDS` dictionary.
        """
        super().__init__(log=log, reply_queue=reply_queue)

    def route_message(self, message):
        
        # assign default actor
        default = ray.get_actor(ACTOR_TYPE.DEFAULT)

        if message.body.startswith("/"):
            command = message.body.split(' ', 1)[0]
            if command in COMMANDS.keys():
                actor = ray.get_actor(COMMANDS[command].value)
                actor.process_message.remote(message)
            if command == '/clear':
                reply_message = ClearMessage()
                self.reply_queue.put(reply_message)
        else:
            default.process_message.remote(message)

