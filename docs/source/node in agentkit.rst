Node in AgentKit
=====

The basic building block in AgentKitMulti is a *node*, containing a natural language prompt for a specific subtask.
The nodes are linked together by the dependency specifications, which specify the order of evaluation.
Different arrangements of nodes can represent different different logic and throught processes.
At inference time, AgentKitMulti evaluates all nodes in the order specified by the dependencies as a directed acyclic graph (DAG).

Inside a Node
----------------

.. autoclass:: agentkitmulti.node.BaseNode
    :special-members: __init__

Inside each node :math:`v`, AgentKitMulti runs a built-in flow that preprocesses the input (Compose), queryies the LLM with a preprocessed input and prompt :math:`q_v`, and optionally postprocesses the output of the LLM (After-query).
For example, node :math:`n_{4}` can be designed to Identify the intentions of other road users. (left of Figure).

.. figure:: https://github.com/Holmeswww/AgentKit/raw/main/imgs/node_archi.png
    :scale: 80 %
    :alt: Illustration of what's happening inside a node in AgentKit

    Each node in AgentKitMulti takes outputs from its dependencies and outputs a string to complete a predefined subtask. The orange components (After-query) are optional and can be further customized with minimal programming through the AgentKitMulti API. 
    **Left**: The evaluation process inside a node consists of compose and after-query. 

Compose
----------------
.. autoclass:: agentkitmulti.compose_prompt.BaseComposePrompt
    :special-members: __init__
    :members:

The Compose operation is a built-in operation that preprocesses the input before querying the LLM.
The Compose operation is designed to be customizable with minimal programming through the AgentKitMulti API.
For example, the Compose operation can be used to add a prefix to the input, remove irrelevant information, or add additional context to the input.

.. autoclass:: agentkitmulti.compose_prompt.ComposePromptDB
    :special-members: __init__
    :members:

The Compose operation can take a database and perform retrival augmented generation (RAG).
The database can be used to store and retrieve:
    - Permanent information like system prompts, user preferences, or context information.
    - External information like multi-modal environment observations, interaction history.
    - Temporary information like previous plan/strategy, intermediate results, user inputs.

After-query
----------------
.. autoclass:: agentkitmulti.after_query.BaseAfterQuery
    :special-members: __init__
    :members:

The After-query operation is a optional operation that postprocesses the output of the LLM.

.. autoclass:: agentkitmulti.after_query.JsonAfterQuery
    :special-members: __init__
    :members:

For example, the JsonAfterQuery operation can be used to extract structured information from the LLM output, and store them in a database for future use.