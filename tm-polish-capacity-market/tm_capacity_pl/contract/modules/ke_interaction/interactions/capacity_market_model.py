from typing import Union

from ke_client import BindingsBase, ki_object, ki_split_uri, SplitURIBase
from rdflib import URIRef, Literal


@ki_object("baseline-flexibility")
class BaselineFlexRequest(BindingsBase):
    ts_uri: URIRef
    dp: URIRef
    ts: Literal
    dpr: URIRef
    value: Union[URIRef, Literal, None]


@ki_object("baseline-flexibility", result=True)
class BaselineFlexResponse(BindingsBase):
    flex_instruction: URIRef
    power_offer: URIRef
    cost_dp: URIRef
    cost_dpr: URIRef
    cost_value: Union[URIRef, Literal, None]
    offer_dp: URIRef
    offer_ts: Literal
    offer_dpr: URIRef
    offer_value: Union[URIRef, Literal, None]


@ki_object("baseline")
class Baseline(BindingsBase):
    ts_uri: URIRef
    dp: URIRef
    ts: Literal
    dpr: URIRef
    value: Union[URIRef, Literal, None]


@ki_object("capacity-market-price")
class MarketPrice(BindingsBase):
    offer_uri: URIRef
    dp: URIRef
    ts: Literal
    dpr: URIRef
    duration_uri: URIRef
    duration: Literal
    value: Union[URIRef, Literal, None]


#############################################################################
@ki_split_uri(uri_template="/price")
class MarketOfferUri(SplitURIBase):
    pass


@ki_split_uri(uri_template="/year/${year}/${quarter}")
class DurationURI(SplitURIBase):
    year: int
    quarter: int = 0



@ki_split_uri(uri_template="/dp/${year}/${quarter}")
class MarketOfferDPUri(SplitURIBase):
    year: int
    quarter: int = 0


@ki_split_uri(uri_template="/dpr/${year}/${quarter}")
class MarketOfferDPRUri(SplitURIBase):
    isp: int


#############################################################################
@ki_split_uri(uri_template="/request/${ts}")
class FlexRequestUri(SplitURIBase):
    ts: int


@ki_split_uri(uri_template="/baseline/${ts}")
class BaselineUri(SplitURIBase):
    ts: int


@ki_split_uri(uri_template="/dp/${isp}")
class BaselineDPUri(SplitURIBase):
    isp: int


@ki_split_uri(uri_template="/dpr/${isp}")
class BaselineDPRUri(SplitURIBase):
    isp: int


#####################

@ki_object("contract")
class TMContract(BindingsBase):
    flex_request: URIRef
    flex_offer: URIRef
    flex_participant: URIRef
    flex_dp: URIRef
    cost_dp: URIRef
    flex_dpr: URIRef
    cost_dpr: URIRef
    ts: Literal
    dpr: URIRef
    flex_value: Union[URIRef, Literal, None]
    cost_value: Union[URIRef, Literal, None]


@ki_object("contract-ack")
class TMContractACK(BindingsBase):
    flex_request: URIRef
    flex_offer: URIRef
    flex_participant: URIRef
    flex_dp: URIRef
    cost_dp: URIRef
    flex_dpr: URIRef
    cost_dpr: URIRef
    ts: Literal
    dpr: URIRef
    flex_value: Union[URIRef, Literal, None]
    cost_value: Union[URIRef, Literal, None]

