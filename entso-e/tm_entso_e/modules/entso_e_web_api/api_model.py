from typing import Annotated, List, Optional

from pydantic import Field
from setuptools.errors import BaseError

from tm_entso_e.modules.entso_e_web_api.utils import XMLBaseModel


class PeriodInterval(XMLBaseModel):
    start: str
    end: str


class Point(XMLBaseModel):
    position: Annotated[int, Field(alias='position')]
    price: Annotated[float, Field(alias='price.amount')]


class Period(XMLBaseModel):
    time_interval: Annotated[PeriodInterval, Field(alias='timeInterval')]
    resolution: Annotated[str, Field(alias='resolution')]
    points: Annotated[List[Point], Field(alias='Point')]


class TimeSeries(XMLBaseModel):
    m_rid: Annotated[str, Field(alias='mRID')]
    auction_type: Annotated[str, Field(alias='auction.type')]
    business_type: Annotated[str, Field(alias='businessType')]
    currency_unit: Annotated[str, Field(alias='currency_Unit.name')]
    measurement_unit: Annotated[str, Field(alias='price_Measure_Unit.name')]
    sequence: Annotated[
        Optional[str], Field(alias='classificationSequence_AttributeInstanceComponent.position', default=None)]
    periods: Annotated[List[Period], Field(alias='Period')]


# <in_Domain.mRID codingScheme="A01">10YPL-AREA-----S</in_Domain.mRID>
# <out_Domain.mRID codingScheme="A01">10YPL-AREA-----S</out_Domain.mRID>
# <contract_MarketAgreement.type>A01</contract_MarketAgreement.type>
# <currency_Unit.name>EUR</currency_Unit.name>
# <curveType>A03</curveType>


class MarketDocument(XMLBaseModel):
    m_rid: Annotated[str, Field(alias='mRID')]
    revision_number: Annotated[int, Field(alias='revisionNumber')]
    document_type: Annotated[str, Field(alias='type')]
    create_date_time: Annotated[str, Field(alias='createdDateTime')]
    time_interval: Annotated[PeriodInterval, Field(alias='period.timeInterval')]
    timeseries: Annotated[List[TimeSeries], Field(alias='TimeSeries')]


class MarketDocumentErrorReason(XMLBaseModel):
    code: int
    text: str


class MarketDocumentError(XMLBaseModel):
    m_rid: Annotated[str, Field(alias='mRID')]
    create_date_time: Annotated[str, Field(alias='createdDateTime')]
    reason: Annotated[MarketDocumentErrorReason, Field(alias='Reason')]


class APIBaseError(BaseError):
    __ctx__: Optional[str]
    __message__: Optional[str]

    def __init__(self, message: str, *args, ctx: str, **kwargs):
        super().__init__(message, *args)
        self.__ctx__ = ctx
        self.__message__ = message

    def __str__(self):
        return f"{self.__ctx__} - {self.__message__}"


class APIError(APIBaseError, TypeError):
    def __init__(self, code: str, text: str, *args, ctx: str, **kwargs):
        super().__init__(f"code: {code}, details: '{text}'", *args, ctx=ctx, **kwargs)
