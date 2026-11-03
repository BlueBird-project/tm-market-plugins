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