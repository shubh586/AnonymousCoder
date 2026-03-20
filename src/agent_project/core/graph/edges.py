from ..states.AnonymousState import AnonymousState


def route_edge(state: AnonymousState):
    """Route to execution_node or scaffolding_node based on query classification."""
    query_type = state.get("type", "execution_node")
    if query_type == "scaffolding_node":
        return "scaffolding_node"
    return "execution_node"