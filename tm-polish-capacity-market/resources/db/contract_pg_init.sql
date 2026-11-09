 DROP TABLE IF EXISTS "${table_prefix}flex_request";
CREATE TABLE "${table_prefix}flex_request" (
    request_uri VARCHAR(250) PRIMARY KEY,
    offer_period_uri VARCHAR(250) NOT NULL,
    create_ts BIGINT NOT NULL,
    ts_from BIGINT NOT NULL,
    ts_to BIGINT NOT NULL
);

CREATE UNIQUE INDEX "${table_prefix}flex_request_create_ts"
    ON "${table_prefix}flex_request" (create_ts);


CREATE TABLE "${table_prefix}flex_offer" (
        flex_request_uri VARCHAR(250) NOT NULL,
        asset_manager_uri VARCHAR(250) NOT NULL,
        flex_profile_uri VARCHAR(250) NOT NULL,
        profile_price_uri VARCHAR(250) NOT NULL,
        flex_price DOUBLE PRECISION,
        ts BIGINT,
        flex_value DOUBLE PRECISION,
        cost_value DOUBLE PRECISION,
        update_ts BIGINT,
        cost_update_ts BIGINT,
        CONSTRAINT uq_flex_offer_request_asset
            UNIQUE (flex_request_uri, asset_manager_uri)
    );
