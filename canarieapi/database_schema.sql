CREATE TABLE IF NOT EXISTS stats (
  route VARCHAR(32) PRIMARY KEY,
  invocations INTEGER,
  last_access TIMESTAMP);

CREATE TABLE IF NOT EXISTS  status (
  route VARCHAR(32),
  service VARCHAR(32),
  status VARCHAR(8),
  message VARCHAR(256),
  PRIMARY KEY (route, service)
  );

CREATE TABLE IF NOT EXISTS cron (
  job VARCHAR(32) PRIMARY KEY,
  last_execution TIMESTAMP);

CREATE TABLE IF NOT EXISTS raw_stats(
    call_date TIMESTAMP,
    ip VARCHAR(15),
    call_count INTEGER,
    primary key (call_date,ip)
);

CREATE TABLE IF NOT EXISTS ip_details(
    ip VARCHAR(15),
    asn BIGINT,
    asn_description VARCHAR(50),
    asn_country CHAR(2),
    last_updated TIMESTAMP,
    PRIMARY KEY (ip,asn_description)
);


CREATE TABLE IF NOT EXISTS unprocessed_ips(
  ip VARCHAR(15) PRIMARY KEY
  );
