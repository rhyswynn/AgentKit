import requests, re
try:
    import bs4
except ImportError:
    raise ImportError("Please install bs4 to use URL helpers.")

from bs4 import BeautifulSoup
from agentkitmulti.exceptions import AfterQueryError
from agentkitmulti.node_functions import error_msg_default
from collections.abc import Callable, Awaitable
from agentkitmulti.base_node import BaseNode
from agentkitmulti.graph import Graph
from agentkitmulti.after_query import BaseAfterQuery
from agentkitmulti.compose_prompt import BaseComposePrompt
from colorama import Fore, Back, Style
import copy
import datetime
try:
    from wandb.sdk.data_types.trace_tree import Trace
except:
    pass

class URLQuery:
    """Base class for URL Queries.

    Each after query instance performs postprocessing after the LLM query.

    Attributes:
        url (str): URL to be retrieved.
    """
    def __init__(self,props:dict = None):
        self.props = props

    def auth(self):
        """Perform authorization procedure

        This method is not implemented in the base class
        """
        return None

    def pre_process(self):
        """Perform preliminary steps that may be needed to successfully query the 
        target endpoint.

        This method is not implemented in the base class
        """
        return None
    
    def post_process(self,response):
        """Post process the result of the URL query.

        This method is not implemented im the base class
        """
        soup = BeautifulSoup(response.content, "html.parser")
        result = soup.get_text()
        return result
    
    def url_query(self):
        response = requests.get(self.props['url'])
        result = response
        return result
    
    def __call__(self, props):
        self.props = props
        result = self.url_query()
        return result

class WeatherQuery(URLQuery):
    """Class for querying US Weather

    Each after query instance performs postprocessing after the LLM query.

    Attributes:
        url (str): URL to be retrieved.
    """        
    def post_process(self,response):
        """Post process the result of the URL query for Weather.com.
        This method can be overridden by the derived class to perform postprocessing.
        """
        soup = BeautifulSoup(response.content, "html.parser")
        result = re.sub('.*As of','',soup.get_text()).replace('\n\n','')
        result = re.sub('RadarNowMapbox.*','',result)
        result = re.sub("Don't MissVideo.*See MoreAdvertisement",'',result)
        return result
    
    def url_query(self):
        response = requests.get(self.props['url'])
        result = self.post_process(response)
        return result
    
    def __call__(self,prompt):
    #    self.props = props
    #    print(f"self.props is {self.props}")
    #    print(f"props url is {props['url']}")
        result = self.url_query()
        return result
    
class ADOQuery(URLQuery):
    """Class for querying US Weather

    Each after query instance performs postprocessing after the LLM query.

    Attributes:
        url (str): URL to be retrieved.
    """        
    def post_process(self,response):
        """Post process the result of the URL query for Weather.com.
        This method can be overridden by the derived class to perform postprocessing.
        """
        soup = BeautifulSoup(response.content, "html.parser")
        result = re.sub('.*As of','',soup.get_text()).replace('\n\n','')
        result = re.sub('RadarNowMapbox.*','',result)
        result = re.sub("Don't MissVideo.*See MoreAdvertisement",'',result)
        return result
    
    def url_query(self):
        response = requests.get(self.props['url'])
        result = self.post_process(response)
        return result
    
    def __call__(self,prompt):
    #    self.props = props
    #    print(f"self.props is {self.props}")
    #    print(f"props url is {props['url']}")
        result = self.url_query()
        return result
    

class URLNode(BaseNode):
    """Class for a URL node in the graph.

    Each node in the graph is an instance of the BaseNode class. The node is evaluated by querying the LLM with a prompt.

    Attributes:
        key (str): Unique key for the node.
        prompt (str): Prompt for the node.
        result (str): Result of the node evaluation.
        temporary_skip (bool): Flag to skip the node evaluation.
        graph (Graph): Graph object.
        adjacent_to (list): List of nodes that are adjacent to this node.
        adjacent_from (list): List of nodes that are adjacent from this node.
        evaluate_after (list): List of nodes that are evaluated after this node.
        counts (list): List of token counts.
        query_function (Callable): Function to take action in the node.
        _compose_prompt (BaseComposePrompt): ComposePrompt object.
        after_query (BaseAfterQuery): AfterQuery object.
        error_msg_fn (Callable): Function to add error message to the prompt.
        verbose (bool): Verbose flag.
        token_counter (Callable): Function to count tokens.
    """
    def __init__(self, key:str, prompt:str, graph:Graph, query_function:Callable, compose_prompt:BaseComposePrompt, after_query:BaseAfterQuery=None, error_msg_fn:Callable[[list,str,AfterQueryError],list]=error_msg_default, verbose:bool=False, token_counter:Callable=None):
        """Initializes the BaseNode class.
        
        Args:
            key (str): Unique key for the node.
            prompt (str): Prompt for the node.
            graph (Graph): Graph object.
            query_function (Callable): Function to query the LLM.
            query_uri (Callable): Function to query a URI.
            compose_prompt (BaseComposePrompt): ComposePrompt object.
            after_query (BaseAfterQuery): AfterQuery object.
            error_msg_fn (Callable): Function to add error message to the prompt.
            verbose (bool): Verbose flag.
            token_counter (Callable): Function to count tokens.
        """
        self.key = key
        self.prompt = prompt
        self.result = None
        self.temporary_skip = False
        self.temporary_skip = False
        self.graph = graph
        self.adjacent_to = []  # this -> node
        self.adjacent_from = []  # node -> this
        self.evaluate_after = []  # node -> this
        self.counts = []
        self.query_function = query_function
        self._compose_prompt = compose_prompt
        self.after_query = None
        self.chain_span = None
        if after_query is not None:
            self.after_query = after_query
            self.after_query.set_node(self)
        self.verbose = verbose
        self._add_error_msg = error_msg_fn
        
        if token_counter is not None:
            self.token_counter = token_counter
        else:
            self.token_counter = None

    def _query_function(self, prompt):

        start_time_ms = round(datetime.datetime.now().timestamp() * 1000)
        result = self.query_function(prompt)
        end_time_ms = round(datetime.datetime.now().timestamp() * 1000)

        if self.chain_span is not None:
            llm_span = Trace(
                "External",
                kind="uri",
                start_time_ms=start_time_ms,
                end_time_ms=end_time_ms,
                inputs={"prompt":prompt},
                status_code="success",
                outputs={"response": result},
            )
            self.chain_span.add_child(llm_span)
        return result
    
    def _after_query(self, ignore_errors=False):
        if self.after_query is None:
            return
        status_code = "success"
        status_message = ""
        error = None
        after_query_input = self.result
        try:
            start_time_ms = round(datetime.datetime.now().timestamp() * 1000)
            self.after_query()
        except AfterQueryError as e:
            status_code = "error"
            status_message = e.error
            error = e
            self.result = after_query_input
        end_time_ms = round(datetime.datetime.now().timestamp() * 1000)
        if self.chain_span is not None:
            tool_span = Trace(
                "AfterQuery",
                kind="tool",
                status_code=status_code,
                status_message=status_message,
                start_time_ms=start_time_ms,
                end_time_ms=end_time_ms,
                inputs={"input": after_query_input},
                outputs={"response": self.result},
            )
            self.chain_span.add_child(tool_span)
        if status_code == "error":
            if ignore_errors:
                print(Fore.RED + "WARNING: ({}, {}) for {}".format(error, status_message, self.result) + Fore.RESET)
                self.result = "N/A"
            else:
                raise error

    def set_trace(self):
        if self.graph.chain_span is None:
            self.chain_span = None
            return
        chain_span = Trace(
            "NodeChain",
            kind="chain",
            start_time_ms=round(datetime.datetime.now().timestamp() * 1000),
            metadata={"prompt": self.prompt, "key": self.key},
        )
        self.chain_span = chain_span

    def commit_trace(self):
        if self.chain_span is None:
            return
        self.chain_span._span.end_time_ms = round(datetime.datetime.now().timestamp() * 1000)
        self.chain_span.add_inputs_and_outputs(inputs={"dependencies": [(node.key,node.result) for node in self.adjacent_from]}, 
                                               outputs={"response": self.result})
        self.graph.chain_span.add_child(self.chain_span)
        self.chain_span = None

    def evaluate(self):
        """Evaluate the node by querying the LLM.

        Retries the AfterQuery with the LLM up to 3 times in case of an error.

        Returns:
            str: Result of the node evaluation.

        Raises:
            AssertionError: If any dependency of the node has not been evaluated.
        """
        for node in self.adjacent_from:
            assert node.result is not None, "Dependency {} of {} has been not evaluated".format(node.key, self.key)

        if not self.temporary_skip:
            self.set_trace()
            prompt, shrink_idx = self.compose_prompt()
            error = None
            self._print_question()
            for i in range(3):
                try:
                    temp_prompt = copy.deepcopy(prompt)
                    if error is not None:
                        temp_prompt = self._add_error_msg(temp_prompt, self.result, error)
                    self.result = self._query_function(prompt)
                    break
                except AfterQueryError as e:
                    error = e.error
            self.commit_trace()
            self._print_answer(self.result)
            print()
        else:
            self.temporary_skip = False
        return self.result
