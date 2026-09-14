def init_service():
    # if ke is enabled
    from tm_capacity_pl.contract.modules.ke_interaction.interactions.fm_interactions import ki as fm_ki
    from tm_capacity_pl.core import smart_client
    smart_client.include(fm_ki)
