import logging
from logging import Logger
from typing import Optional, Dict

import requests
from pydantic import BaseModel
from xml.etree.ElementTree import Element, ElementTree, parse as parse_xml

from requests import Response


class RESTClient(BaseModel):
    # region private fields
    _logger_: Logger = None
    # verify KE certificate if SSL is on
    _verify_cert_: bool = True
    # state of client
    _timeout_: int = 30

    # endregion

    def __init__(self, logger: Optional[Logger] = None, **kwargs):
        # self._verify_cert_ = verify_cert
        from tm_entso_e.modules.entso_e_api.config import api_settings
        self._logger_ = logging.getLogger() if logger is None else logger
        super().__init__(_timeout_=api_settings.api_timeout, **kwargs)

    @property
    def logger(self):
        return self._logger_

    # region requests

    def _api_send_request_(self, url: str, headers: Dict, register=False) -> Element:
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
                resp_content: ElementTree = parse_xml(response.content)
            except Exception as exc:
                self.logger.error(f"{err}: Error in parsing xml content {response.text}")
                raise Exception("Invalid response")
            resp_content_root: Element = resp_content.find("Acknowledgement_MarketDocument/Reason")
            self.logger.error(f"{err}: {resp_content_root.text} ")

        assert response.ok
        try:
            resp_content: ElementTree = parse_xml(response.content)
        except Exception as err:
            self.logger.error(f"{err}: Error in parsing xml content {response.text}")
            raise Exception("Invalid response")
        return resp_content.getroot()

        # endregion
