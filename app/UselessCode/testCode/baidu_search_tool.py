import json
from typing import Optional, List, Dict, Any

from phi.tools import Toolkit
from phi.utils.log import logger

try:
    from baidusearch.baidusearch import search as baidu_search_api
except ImportError:
    raise ImportError("`baidusearch` not installed. Please install using `pip install baidusearch`")

try:
    from pycountry import pycountry
except ImportError:
    raise ImportError("`pycountry` not installed. Please install using `pip install pycountry`")

class baidusearch(Toolkit):
    """
    BaiduSearch is a toolkit for searching Baidu easily.

    Args:
        fixed_max_results (Optional[int]): A fixed number of maximum results.
        fixed_language (Optional[str]): A fixed language for the search results.
        headers (Optional[Any]): Headers to be used in the search request.
        proxy (Optional[str]): Proxy to be used in the search request.
        timeout (Optional[int]): Timeout for the search request.
        debug (Optional[bool]): Enable debug output.
    """

    def __init__(
        self,
        fixed_max_results: Optional[int] = None,
        fixed_language: Optional[str] = None,
        headers: Optional[Any] = None,
        proxy: Optional[str] = None,
        timeout: Optional[int] = 10,
        debug: Optional[bool] = False,
    ):
        super().__init__(name="baidusearch")
        self.fixed_max_results: Optional[int] = fixed_max_results
        self.fixed_language: Optional[str] = fixed_language
        self.headers: Optional[Any] = headers
        self.proxy: Optional[str] = proxy
        self.timeout: Optional[int] = timeout
        self.debug: Optional[bool] = debug
        self.register(self.baidu_search)

    def baidu_search(self, query: str, max_results: int = 5, language: str = "zh") -> str:
        """
        搜索指定的查询内容。

        Args:
            query (str): 要搜索的查询字符串。
            max_results (int, optional): 返回的最大结果数。默认值为 5。
            language (str, optional): 搜索结果的语言。默认值为 "zh"。
        
        Returns:
            str: 包含搜索结果的 JSON 字符串。
        """
        max_results = self.fixed_max_results or max_results
        language = self.fixed_language or language

        # 解析语言代码
        if len(language) != 2:
            try:
                _language = pycountry.languages.lookup(language)
                language = _language.alpha_2
            except LookupError:
                language = "zh"

        logger.debug(f"Searching Baidu [{language}] for: {query}")

        # 调用 Baidu 搜索 API，移除不支持的参数
        results = baidu_search_api(
            keyword=query,
            num_results=max_results
            # Remove the 'timeout' argument
            # timeout=self.timeout
        )

        res: List[Dict[str, str]] = []
        for idx, item in enumerate(results, 1):
            res.append(
                {
                    "title": item.get('title', ''),
                    "url": item.get('url', ''),
                    "abstract": item.get('abstract', ''),
                    "rank": idx,
                }
            )
        return json.dumps(res, ensure_ascii=False, indent=2)