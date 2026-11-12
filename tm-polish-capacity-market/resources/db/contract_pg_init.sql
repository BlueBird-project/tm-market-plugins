  DROP TABLE IF EXISTS "${table_prefix}asset_manager";
  DROP SEQUENCE IF EXISTS ${table_prefix}asset_manager_id_seq;
  CREATE SEQUENCE ${table_prefix}asset_manager_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;

  CREATE TABLE "public"."${table_prefix}asset_manager" (
      "asset_manager_id" bigint DEFAULT nextval('${table_prefix}asset_manager_id_seq') NOT NULL,
      "asset_manager_uri" character varying(250) NOT NULL,

      CONSTRAINT "${table_prefix}asset_manager_pk" PRIMARY KEY ("asset_manager_id")
  )
  WITH (oids = false);

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
        price_value DOUBLE PRECISION,
        update_ts BIGINT,
        cost_update_ts BIGINT,
        CONSTRAINT uq_flex_offer_request_asset
            UNIQUE (flex_request_uri, asset_manager_uri),

        CONSTRAINT "${table_prefix}fk_asset_manager" FOREIGN KEY (asset_manager_uri)
        REFERENCES "${table_prefix}asset_manager" (asset_manager_uri)
        ON DELETE RESTRICT ON UPDATE CASCADE
    );


CREATE TABLE "${table_prefix}flex_contract" (
        contract_uri VARCHAR(250) PRIMARY KEY,
        flex_request_uri VARCHAR(250) NOT NULL,
        ack_ts BIGINT NOT NULL,
        update_ts BIGINT NOT NULL,
        flex_value DOUBLE PRECISION,
        price_value DOUBLE PRECISION,
        CONSTRAINT "${table_prefix}fk_flex_contract_offer" FOREIGN KEY (flex_request_uri)
        REFERENCES "${table_prefix}flex_offer" (flex_request_uri)
        ON DELETE RESTRICT ON UPDATE CASCADE
    );


