<div align="center">
<img src="https://github.com/rhyswynn/AgentKitMulti/raw/main/imgs/AgentKitMulti.png" width="350px">

**AgentKitMulti: Flow Engineering with Graphs, not Coding**

Based on the wonderful project [[AgentKit]](https://github.com/Holmeswww/AgentKit)

[[Arxiv Paper]](https://arxiv.org/abs/2404.11483)
[[PDF]](https://arxiv.org/pdf/2404.11483.pdf)
[[Docs]](https://agentkit.readthedocs.io/)

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/agentkit-multi)](https://pypi.org/project/agentkit-multi/)
[![PyPI](https://img.shields.io/pypi/v/agentkit-llm)](https://pypi.org/project/agentkit-multi/)
[![PyPI Status](https://static.pepy.tech/badge/agentkit-llm)](https://pepy.tech/project/agentkit-multi)
[![Docs](https://readthedocs.org/projects/agentkit/badge/?version=latest)](https://agentkit.readthedocs.io/en/latest/?badge=latest)
[![GitHub license](https://img.shields.io/github/license/rhyswynn/agentkitmulti)](https://github.com/rhyswynn/AgentKitMulti/blob/main/LICENSE)
______________________________________________________________________
![](https://github.com/rhyswynn/AgentKitMulti/raw/main/imgs/teaser.png)
</div>

<img src="https://github.com/rhyswynn/AgentKitMulti/raw/main/imgs/AgentKitMulti.png" width="65px"> offers a unified framework for explicitly constructing a complex human "thought process" from simple natural language prompts.
The user puts together chains of *nodes*, like stacking LEGO pieces. The chains of nodes can be designed to explicitly enforce a naturally *structured* "thought process".

Different arrangements of nodes could represent different functionalities, allowing the user to integrate various functionalities to build multifunctional agents.

A basic agent could be implemented as simple as a list of prompts for the subtasks and therefore could be designed and tuned by someone *without any programming experience*.


# Contents

- [Installation](#Installation)
- [Getting Started](#Getting-Started)
- [Using Built-in LLM_API](#Built-in-LLM-API)
- [Using AgentKit without Programming Experience](#Using-AgentKit-without-Programming-Experience)
- [Node Components](#Node-Components)
- [Citing AgnetKit](#Citing-AgentKit)

# Installation

Installing the AgentKitMulti stable version is as simple as:
(pending publish to PyPI)
```bash
pip install agentkit-multi
```

To install AgentKitMulti with wandb:

```bash
pip install agentkit-multi[logging]
```

To install AgentKitMulti with built-in LLM-API and all additional actions support:

```bash
pip install agentkit-multi[all]
```

Otherwise, to install the cutting edge version from the main branch of this repo, run:

```bash
git clone https://github.com/rhyswynn/AgentKitMulti && cd AgentKitMulti
pip install -e .
```

# Getting Started

The basic building block in AgentKitMulti is a node, containing a natural language prompt for a specific subtask. The nodes are linked together by the dependency specifications, which specify the order of evaluation. Different arrangements of nodes can represent different different logic and throught processes.

At inference time, AgentKitMulti evaluates all nodes in specified order as a directed acyclic graph (DAG).

```python
import agentkitmulti
from agentkitmulti import Graph, BaseNode

import agentkitmulti.llm_api

LLM_API_FUNCTION = agentkitmulti.llm_api.get_query("gpt-4-turbo")

graph = Graph()

subtask1 = "What are the pros and cons for using LLM Agents for Game AI?" 
node1 = BaseNode(subtask1, subtask1, graph, LLM_API_FUNCTION, agentkit.compose_prompt.BaseComposePrompt())
graph.add_node(node1)

subtask2 = "Give me an outline for an essay titled 'LLM Agents for Games'." 
node2 = BaseNode(subtask2, subtask2, graph, LLM_API_FUNCTION, agentkit.compose_prompt.BaseComposePrompt())
graph.add_node(node2)

subtask3 = "Now, write a full essay on the topic 'LLM Agents for Games'."
node3 = BaseNode(subtask3, subtask3, graph, LLM_API_FUNCTION, agentkit.compose_prompt.BaseComposePrompt())
graph.add_node(node3)

# add dependencies between nodes
graph.add_edge(subtask1, subtask2)
graph.add_edge(subtask1, subtask3)
graph.add_edge(subtask2, subtask3)

result = graph.evaluate() # outputs a dictionary of prompt, answer pairs
```

``LLM_API_FUNCTION`` can be any LLM API function that takes ``msg:list`` and ``shrink_idx:int``, and outputs ``llm_result:str`` and ``usage:dict``. Where ``msg`` is a prompt ([OpenAI format](https://platform.openai.com/docs/guides/text-generation/chat-completions-api) by default), and ``shrink_idx:int`` is an index at which the LLM should reduce the length of the prompt in case of overflow. 

AgentKitMulti tracks token usage of each node through the ``LLM_API_FUNCTION`` with:
```python
usage = {
    'prompt': $prompt token counts,
    'completion': $completion token counts,
}
```

# Built-in LLM-API

The built-in `agentkitmulti.llm_api` functions require installing with `[all]` setting. See [the installation guide](#Installation) for details.

Currently, the built-in API supports Azure OpenAI, OpenAI, and Anthropic, see https://pypi.org/project/openai/ and https://pypi.org/project/anthropic/ for details.

To use the OpenAI models, set environment variables `OPENAI_KEY` and `OPENAI_ORG`. Alternatively, you can put the openai 'key' and 'organization' in the first 2 lines of `~/.openai/openai.key`.

To use the Azure OpenAI models, set environment variables `AZURE_OPENAI_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_VERSION`, and `AZURE_OPENAI_DEPLOYMENT`. Be sure to specify the same model as the deployment is based on.

To use the Anthropic models, set environment variable `ANTHROPIC_KEY`. Alternatively, you can put the anthropic 'key' in 3rd line of `~/.openai/openai.key`.

# Additional Helper Actions

The built-in `agentkitmulti.helpers` functions require installing with `[all]` setting. See [the installation guide](#Installation) for details.

Currently, the additional helpers functions supports URLQuery and URLNode base elements. These are used for interacting with any external service. The callback function accepts a dictionary of properties that can be used for flexible connections. currently an example WeatherQuery is in place that can get current weather details from a pre-defined location.

To use the URL elements, create a properties dictionary and reference the WeatherQuery() function in a URLNode object, passing the dictionary as a parameter:
```python
import agentkitmulti
from agentkitmulti import Graph
from agentkitmulti.helpers.url_query import WeatherQuery, URLNode
graph = Graph()

weatherProps = {}
weatherProps['url'] = 'https://weather.com/weather/today/l/d13581dc3bbd72eb552966ce2b1355f0823288ff9a67cba2763a14973b432b32' # Beaufort

subtask = "What is the weather forecast for Beaufort, SC?"
node = URLNode(subtask, subtask, graph, WeatherQuery(weatherProps), agentkitmulti.compose_prompt.BaseComposePrompt(), verbose=verbose)
graph.add_node(node)
```

# Using AgentKitMulti without Programming Experience

First, follow [the installation guide](#Installation) to install AgentKit with `[all]` setting.

Then, set environment variables `OPENAI_KEY` and `OPENAI_ORG` to be your OpenAI key and org_key.

Finally, run the following to evoke the command line interface (CLI):

```bash
git clone https://github.com/rhyswynn/AgentKitMulti && cd AgentKitMulti
cd examples/prompt_without_coding
python generate_graph.py
```
![](https://github.com/rhyswynn/AgentKitMulti/raw/main/imgs/screenshot.png)

# Node Components

![](https://github.com/rhyswynn/AgentKitMulti/raw/main/imgs/node_archi.png)
Inside each node (as shown to the left of the figure), AgentKitMulti runs a built-in flow that **preprocesses** the input (Compose), queries the LLM with a preprocessed input and prompt $q_v$, and optionally **postprocesses** the output of the LLM (After-query).

To support advanced capabilities such as branching, AgentKitMulti offers API to dynamically modify the DAG at inference time (as shown to the right of the figure). Nodes/edges could be dynamically added or removed based on the LLM response at some ancestor nodes.

# Citing AgentKit

Full credit and the greatest admiration and appreciation for the original authors, and to Holmeswww for this contribution to the open source community!

```bibtex
@article{wu2024agentkit,
    title={AgentKit: Flow Engineering with Graphs, not Coding}, 
    author={Yue Wu and Yewen Fan and So Yeon Min and Shrimai Prabhumoye and Stephen McAleer and Yonatan Bisk and Ruslan Salakhutdinov and Yuanzhi Li and Tom Mitchell},
    year={2024},
    journal={arXiv preprint arXiv:2404.11483}
}
```

# Star History

<a href="https://star-history.com/#rhyswynn/agentkitmulti&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=rhyswynn/agentkitmulti&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=rhyswynn/agentkitmulti&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=rhyswynn/agentkitmulti&type=Date" />
 </picture>
</a>