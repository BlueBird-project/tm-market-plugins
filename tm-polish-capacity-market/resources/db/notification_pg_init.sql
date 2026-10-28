

 DROP TABLE IF EXISTS "${table_prefix}asset_manager";
 DROP SEQUENCE IF EXISTS ${table_prefix}asset_manager_id_seq;
 CREATE SEQUENCE ${table_prefix}asset_manager_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;

 CREATE TABLE "public"."${table_prefix}asset_manager" (
     "asset_manager_id" bigint DEFAULT nextval('${table_prefix}asset_manager_id_seq') NOT NULL,
     "asset_manager_uri" character varying(250) NOT NULL,

     CONSTRAINT "${table_prefix}asset_manager_pk" PRIMARY KEY ("asset_manager_id")
 )
 WITH (oids = false);

 DROP TABLE IF EXISTS "${table_prefix}flex_contract";

 CREATE TABLE "public"."${table_prefix}flex_contract" (
     "asset_manager_id" bigint  NOT NULL,
     "flex_request_uri" character varying(250) NOT NULL,
     "contract_uri" character varying(250) NOT NULL,
     "market_uri" character varying(250) NOT NULL,
     "flex_dp_uri" character varying(250) NOT NULL,
     "cost_dp_uri" character varying(250) NOT NULL,
     "flex_dpr_uri" character varying(250) NOT NULL,
     "cost_dpr_uri" character varying(250) NOT NULL,
     "flex_value" double precision NOT NULL,
     "cost_value" double precision NOT NULL,
     "period_uri_uri" character varying(250) NOT NULL,
     "ts_date_from" bigint  NOT NULL,
     "ts_date_to" bigint  NOT NULL,
     "ts" bigint  NOT NULL,
      "ack"  boolean default FALSE  ,
      "ack_ts"  bigint    ,
      "update_ts"  bigint  NOT NULL,
          CONSTRAINT "${table_prefix}flex_contract_pk" PRIMARY KEY ("contract_uri")
 )

WITH (oids = false);

CREATE INDEX "${table_prefix}flex_contract_asset_manager_id_ts" ON "${table_prefix}flex_contract" ("asset_manager_id", "ts");
ALTER TABLE "${table_prefix}flex_contract" ADD FOREIGN KEY ("asset_manager_id") REFERENCES "${table_prefix}asset_manager" ("asset_manager_id") ON DELETE RESTRICT ON UPDATE CASCADE NOT DEFERRABLE;


 DROP TABLE IF EXISTS "${table_prefix}market_notification";
 DROP SEQUENCE IF EXISTS ${table_prefix}notification_id_seq;
 CREATE SEQUENCE ${table_prefix}notification_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;

 CREATE TABLE "public"."${table_prefix}market_notification" (
     "notification_id" bigint DEFAULT nextval('${table_prefix}notification_id_seq') NOT NULL,
     "email" character varying(20000) NOT NULL,
     "date" character varying(10) NOT NULL,
     "isp"  int NOT NULL,
     "ts"  bigint NOT NULL,

      CONSTRAINT "${table_prefix}market_notification_k" PRIMARY KEY ("notification_id")
 )

WITH (oids = false);

CREATE TABLE "${table_prefix}ke_notification" (
    "asset_manager_id" BIGINT NOT NULL,
    "flex_instruction_uri" VARCHAR(250) NOT NULL,
    "flex_offer_uri" VARCHAR(250) NOT NULL,
    "flex_profile_uri" VARCHAR(250) NOT NULL,
    "power_limit_uri" VARCHAR(250) NOT NULL,
    "ts" BIGINT NOT NULL,
    "max_consumption_uri" VARCHAR(250) NOT NULL,
    "max_consumption_value" DOUBLE PRECISION NOT NULL,
    "update_ts" BIGINT NOT NULL,

    CONSTRAINT "${table_prefix}ke_notification_notification_instruction_ts"    UNIQUE ("flex_instruction_uri", "ts")
);

ALTER TABLE "${table_prefix}ke_notification" ADD FOREIGN KEY ("asset_manager_id") REFERENCES "${table_prefix}asset_manager" ("asset_manager_id") ON DELETE RESTRICT ON UPDATE CASCADE NOT DEFERRABLE;
