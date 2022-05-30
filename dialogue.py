# utility for storing dialogue in trees
# credit to https://stackoverflow.com/questions/68747114/discord-py-how-to-make-clean-dialog-trees
import asyncio
import typing

NodeID = str
ABORT = 'goodbye'


class BadFSMError(ValueError):
    """class for exceptions related to FSM/Dialogue Tree"""


class NoEntryNodeError(BadFSMError):
    """entry node wasn't set in FSM"""


class RoadToNowhereError(BadFSMError):
    """wound up falling off the tree to a forbidden node"""


class Node:
    def __init__(self,
                 prompt: typing.Optional[str],
                 choices: typing.Mapping[str, typing.Tuple[NodeID, typing.Callable[[typing.Any], None]]],
                 delay: int = 2, is_exit: bool = False):
        self.prompt = prompt
        self.choices = choices
        self.delay = delay
        self.is_exit = is_exit

    async def get_next(self, message) -> typing.Optional[NodeID]:
        """get input and move to next dialogue"""

        # wait appropriate amount of time while "Typing..", followed by prompt
        async with message.channel.typing():
            await asyncio.sleep(self.delay)
        if self.prompt:
            await message.channel.send(self.prompt)

        if self.is_exit:
            return None

        # TODO: get user choice from chat or select menu
        choice = 'good choice'  # placeholder
        result = self.choices[choice]
        if isinstance(result, tuple):
            next_id, mod_func = self.choices[choice]
            mod_func(self)
        else:
            next_id = result
        return next_id


NODES = {
    'start': Node("Oh, hey, it’s you! Ground control didn’t tell me you were launching. Long time no see!\n"
                  "Actually, I guess it’s been a long time since I’ve seen anyone.",
                  {}, is_exit=True)
}


class DialogueTree:
    # Finite state machine (thanks CS240) - dialogue tree stores status as current node
    def __init__(self, nodes=None, entry_node=None):
        if nodes is None:
            nodes = {}
        self.nodes: typing.Mapping[NodeID, Node] = nodes
        # a NodeID, not a Node
        self.entry_node = entry_node

    def add_node(self, nid: NodeID, node: Node):
        if nid in self.nodes:
            raise ValueError(f"Node with ID {nid} already exists!")
        self.nodes[nid] = node

    def set_entry(self, nid: NodeID):
        if nid not in self.nodes:
            raise ValueError(f"Attempting to set unknown node {nid} as entry")
        self.entry_node = nid

    async def evaluate(self, message):
        # begin FSM at message and move through dialogue tree
        if not self.entry_node:
            raise NoEntryNodeError

        # start at entry node
        current = self.nodes[self.entry_node]
        while current is not None:
            next_nid = await current.get_next(message)
            if next_nid is None:
                return
            if next_nid not in self.nodes:
                raise RoadToNowhereError
            current = self.nodes[next_nid]
