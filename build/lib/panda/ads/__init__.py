import traceback
from aiohttp import (ClientSession, ClientTimeout, TCPConnector)
from typing import Tuple, Literal

DEFAULT_TIMEOUT = ClientTimeout(total=1 * 60)
DEFAULT_TCP_SSL = False


class Config:

    def __init__(self, proxy: str, token: str, proxy_type="http"):
        """
        init
        :param proxy: ip and port
        :param proxy_type: http or https
        :param token: secret token
        """
        self.proxy: str = f"{proxy_type}://{str(proxy)}"
        self.token: str = token


class Pandas:

    def __init__(self, config: Config, timeout: ClientTimeout = DEFAULT_TIMEOUT, is_ssl: bool = DEFAULT_TCP_SSL):
        """
        :param config: Config Class
        :param timeout: default http/https timeout time (60s)
        :param is_ssl:  default ssl method (FALSE)
        """
        self.__token = config.token
        self.__proxy = config.proxy
        self.__headers = {'Content-Type': 'application/json'}
        self.__timeout = timeout
        self.__is_ssl = is_ssl

    async def async_request(self, url: str, payload: dict = None,
                            method: Literal["GET", "POST"] = "GET") -> Tuple[int, str, dict]:
        """
        :param method: Request method, either "GET" or "POST".
        :param url: Target URL for the request
        :param payload: Parameters to send with the request.
        :return: A tuple containing the response status code, a message, and the response body as a dictionary.
        """
        response_code, response_msg, response_body = -1, str(), dict()
        try:
            payload["access_token"] = self.__token
            # Create an asynchronous HTTP client session with SSL/TLS support and a specified timeout
            async with ClientSession(connector=TCPConnector(ssl=self.__is_ssl), timeout=self.__timeout) as session:
                # Send a GET request to the specified URL with parameters, headers, and proxies
                method_handler = {"GET": session.get, "POST": session.post}[method]
                async with method_handler(url, json=payload, headers=self.__headers, proxy=self.__proxy) as response:
                    # Parse the response body as a JSON dictionary
                    response_body: dict = await response.json(encoding="utf-8")
                    response_code = response.status
        except Exception as e:
            response_msg = traceback.format_exc()
            raise e
        finally:
            # Return the status code and response body
            return response_code, response_msg, response_body
