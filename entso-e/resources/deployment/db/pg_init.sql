--DROP TABLE IF EXISTS "${table_prefix}app_config";
--CREATE TABLE "public"."${table_prefix}app_config" (
--    "key" text NOT NULL,
--    "value" text ,
--    "update_ts" bigint ,
--    CONSTRAINT "tm_config_text" PRIMARY KEY ("key")
--)
--WITH (oids = false);

DROP TABLE IF EXISTS "${table_prefix}market_details";
DROP SEQUENCE IF EXISTS ${table_prefix}market_details_market_id_seq;
CREATE SEQUENCE ${table_prefix}market_details_market_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;

CREATE TABLE "public"."${table_prefix}market_details" (
    "market_id" bigint DEFAULT nextval('${table_prefix}market_details_market_id_seq') NOT NULL,
    "market_uri" character varying(250) NOT NULL,
    "market_name" character varying(50) NOT NULL,
    "market_type" character varying(30) NOT NULL,
    "market_description" character varying(50),
    "market_location" character varying(250),
    "subscribe" 	boolean  ,
    "update_ts" bigint NOT NULL,
    "ext" character varying(10000),
    CONSTRAINT "${table_prefix}market_details_key" PRIMARY KEY ("market_id")
)
WITH (oids = false);

CREATE UNIQUE INDEX ${table_prefix}market_details_market_uri ON public.${table_prefix}market_details USING btree (market_uri);


DROP TABLE IF EXISTS "${table_prefix}market_offer_details";
DROP SEQUENCE IF EXISTS ${table_prefix}market_offer_details_offer_id_seq;
CREATE SEQUENCE ${table_prefix}market_offer_details_offer_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;

CREATE TABLE "public"."${table_prefix}market_offer_details" (
    "offer_id" bigint DEFAULT nextval('${table_prefix}market_offer_details_offer_id_seq') NOT NULL,
    "market_id" bigint NOT NULL,
    "sequence" int  ,
    "currency_unit" character varying(10) NOT NULL,
    "volume_unit" character varying(10) NOT NULL,
    "ts_start" bigint NOT NULL,
    "ts_end" bigint NOT NULL,
    "isp_unit" int NOT NULL,
    "update_ts" bigint NOT NULL,
    "ext" character varying(10000),
    CONSTRAINT "${table_prefix}market_offer_details_key" PRIMARY KEY ("offer_id")
)
WITH (oids = false);

CREATE UNIQUE  INDEX ${table_prefix}market_offer_details_market ON public.${table_prefix}market_offer_details USING btree (market_id,ts_start,sequence);

ALTER TABLE ONLY "public"."${table_prefix}market_offer_details"
ADD CONSTRAINT "${table_prefix}market_offer_details_market_id_fkey" FOREIGN KEY (market_id)
REFERENCES ${table_prefix}market_details(market_id) ON UPDATE RESTRICT ON DELETE RESTRICT NOT DEFERRABLE;


DROP TABLE IF EXISTS "${table_prefix}market_offer";
CREATE TABLE "public"."${table_prefix}market_offer" (
	"ts" bigint NOT NULL,
	"offer_id" bigint NOT NUll,
	"update_ts" bigint NOT NULL ,
	"isp_start" INT NOT NULL,
	"isp_len" INT NOT NULL,
	"cost"  double precision,
    CONSTRAINT "${table_prefix}market_offer_key" PRIMARY KEY ("offer_id","ts","isp_start" )
)
WITH (oids = false);

ALTER TABLE ONLY "public"."${table_prefix}market_offer"
ADD CONSTRAINT "${table_prefix}market_offer_offer_id_fkey" FOREIGN KEY (offer_id)
REFERENCES ${table_prefix}market_offer_details(offer_id) ON UPDATE RESTRICT ON DELETE RESTRICT NOT DEFERRABLE;