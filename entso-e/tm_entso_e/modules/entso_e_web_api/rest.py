import datetime
import logging
import re
from logging import Logger
from typing import Optional, Dict

import requests
from pydantic import BaseModel
from xml.etree.ElementTree import Element, ElementTree
import xml.etree.ElementTree as ET

from requests import Response

from tm_entso_e.modules.entso_e_web_api import DATE_FORMAT, ApiKeys
from tm_entso_e.utils import time_utils


def _get_ns(el: Element) -> str:
    match = re.match(r'\{(.*)}', el.tag)
    namespace = match.group(1) if match else ""
    return namespace


class RESTClient(BaseModel):
    # region private fields
    _logger_: Logger = None
    # verify KE certificate if SSL is on
    _verify_cert_: bool = True
    # state of client
    _timeout_: int = 30
    _token_: str
    _endpoint_: str

    # endregion

    def __init__(self, logger: Optional[Logger] = None, **kwargs):
        # self._verify_cert_ = verify_cert
        from tm_entso_e.modules.entso_e_web_api.config import service_settings
        self._logger_ = logging.getLogger() if logger is None else logger
        super().__init__(**kwargs)
        self._token_ = service_settings.token
        self._timeout_ = service_settings.api_timeout
        self._endpoint_ = service_settings.endpoint

    @property
    def logger(self):
        return self._logger_

    # region requests
    def send_request(self, parameters: Dict[str, str]):
        parameters[ApiKeys.security_token] = self._token_
        # TODO: validate all parameters keys
        api_args = "&".join([f"{k}={v}" for k, v in parameters.items()])
        url = f"{self._endpoint_}?{api_args}"
        resp_content = self._api_send_request_(url=url, headers={})
        return resp_content


    # endregion
    # region requests core

    def _api_send_request_(self, url: str, headers: Dict) -> Element:
        try:
            headers["Content-Type"] = "application/xml"
            response: Response = requests.get(url, headers=headers, timeout=self._timeout_, verify=self._verify_cert_)
            return self._assert_response_(response=response)
        except Exception as ex:
            logging.error(f"Connection issue {url} : {ex} ")

    def _assert_response_(self, response: requests.Response) -> Element:
        """
        check if the response from the API is correct and parse if reponse is ok
        :param response: response from API
        :return:
        """

        if not response.ok:
            err = f"Invalid response for {response.url}: {response.status_code}"
            # resp_content = None
            try:
                resp_content: Element = ET.fromstring(response.content)
            except Exception as exc:
                self.logger.error(f"{err}: Error in parsing xml content {response.text}")
                raise Exception("Invalid response")
            # resp_content_root: Element = resp_content.find("Acknowledgement_MarketDocument/Reason")
            # TODO: process this xml with error
            self.logger.error(f"{err}: {resp_content.text} ")

        assert response.ok
        try:
            resp_content: Element = ET.fromstring(response.content)
        except Exception as err:
            self.logger.error(f"{err}: Error in parsing xml content {response.text}")
            raise Exception("Invalid response")
        return resp_content

        # endregion

    @staticmethod
    def parse_time(ts: int) -> str:
        return time_utils.format_timestamp(ts, date_format=DATE_FORMAT)
