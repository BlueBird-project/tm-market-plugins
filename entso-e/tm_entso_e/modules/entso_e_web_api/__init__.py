# __DATE_FORMAT__ = """%d-%m-%y"""
# __DATE_WRITE_FORMAT__ = """%d-%m-%y"""
import logging

from tm_entso_e.schemas.market_dao import MarketDAO

# ENTSOE date format: "yyyyMMddHHmm"
DATE_FORMAT = "%Y%m%d%H%M"


class ApiKeys:
    security_token = "securityToken"
    document_type = "documentType"
    period_start = "periodStart"
    period_end = "periodEnd"
    out_domain = "out_Domain"
    in_domain = "in_Domain"
    market_contract_type = "contract_MarketAgreement.type"
    # classification_sequence_position="classificationSequence_AttributeInstanceComponent.position"
    offset = "offset"


class EICAreaType:
    BZN = "BZN"
    codes = {"BZN": "Bidding Zone"}


#     Code 	Area Type 	Description
# BZN 	Bidding Zone 	Bidding Zone means the largest geographical area within which Market Participants are able to exchange energy without Capacity Allocation
# BZA 	Bidding Zone Aggregation
# CTA 	Control Area 	A coherent part of the interconnected system, operated by a single system operator and shall include connected physical loads and/or generation units if any.
# MBA 	Market Balance Area 	A geographic area consisting of one or more Metering Grid Areas with common market rules for which the settlement responsible party carries out a balance settlement and which has the same price for imbalance. A Market Balance Area may also be defined due to bottlenecks.
# IBA 	Imbalance Area 	The Imbalance Price Area or a part of an Imbalance Price Area, for the calculation of an Imbalance.
# IPA 	Imbalance Price Area 	Either a Bidding Zone, part of a Bidding Zone or a combination of several Bidding Zones, to be defined by each TSO, for the purpose of calculation of Imbalance Prices.
# LFA 	Load Frequency Control Area
# LFB 	Load Frequency Control Block 	The composition of one or more Control Areas, working together to ensure the load frequency control on behalf of RGCE.
# REG 	Region
# SCA 	Scheduling Area 	The Bidding Zone except if there is more than one Responsibility Area within this Bidding Zone. In the latter case, the Scheduling Area equals Responsibility Area or a group of Responsibility Areas
# SNA 	Synchronous Area 	Synchronous Area means an area covered by interconnected Transmission System Operators (TSOs) with a common System Frequency in a steady state
# https://transparencyplatform.zendesk.com/hc/en-us/articles/15885757676308-Area-List-with-Energy-Identification-Code-EIC

def add_market(market: MarketDAO, save_add: bool = True) -> MarketDAO:
    from tm_entso_e.core.db.postgresql import dao_manager
    if save_add:
        db_market = dao_manager.market_api.get_market_uri(market_uri=market.market_uri)
        if db_market is not None:
            market.market_id = db_market.market_id
            dao_manager.market_api.update_market(market=market)
            return db_market
    return dao_manager.market_api.add_market(market=market)


def init_db(market_prefix: str):
    from tm_entso_e.modules.entso_e_web_api.config import api_settings
    from tm_entso_e.modules.entso_e_web_api.service import unsubscribe_all_markets

    unsubscribe_all_markets()

    # or delete all of them >
    for s_eic_area in api_settings.subscribed_eic:
        for market_code in s_eic_area.market_codes:
            # TODO: support more than one country code/location
            market_location = api_settings.eic_codes[s_eic_area.code].country_codes[0]
            from tm_entso_e.modules.ke_interaction.interactions.dam_model import MarketURI
            market = MarketDAO(market_uri=MarketURI(eic_area=s_eic_area.code, market_code=market_code).uri,
                               market_name=s_eic_area.code + "_" + market_code,
                               market_type=s_eic_area.get_market_type_name(code=market_code),
                               market_location=market_location,
                               subscribe=True)
            add_market(market=market)
            logging.info(f"Setting market: {market}")
            # print(market)
