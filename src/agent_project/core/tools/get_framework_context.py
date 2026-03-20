from enum import Enum

from langchain_core.tools import tool

from .frameworks.templates import templates


class FRAMEWORKS(str,Enum):
    NEXT_JS_TEMPLATE="next_js_template",
    VUE_JS_TEMPLATE="vue_js_template",
    REACT_TEMPLATE="react_template",
    REACT_WITH_NODE_JS_TEMPLATE="react_with_node_js_template",
    REACT_WITH_VITE_TEMPLATE="react_with_vite_template",
    REMIX_JS_TEMPLATE="remix_js_template",
    ANGULAR_JS_TEMPLATE="angular_js_template"

@tool
def get_framework_context(framework:FRAMEWORKS):
    """_summary_

    Args:
        framework (FRAMEWORKS): _description_

    Returns:
        _type_: _description_
    """
    context=templates.get(framework)
    return context