CREATE TABLE IF NOT EXISTS [stats] (
  [route] VARCHAR(32),
  [invocations] INTEGER,
  [last_access] DATETIME
);

CREATE UNIQUE INDEX IF NOT EXISTS [stats_id] ON [stats] ([route]);

CREATE TABLE IF NOT EXISTS [status] (
  [route] VARCHAR(32),
  [service] VARCHAR(32),
  [status] VARCHAR(8),
  [message] VARCHAR(256)
);

CREATE UNIQUE INDEX IF NOT EXISTS [status_id] ON [status] ([route], [service]);

CREATE TABLE IF NOT EXISTS [cron] (
  [job] VARCHAR(32),
  [last_execution] DATETIME
);

CREATE UNIQUE INDEX IF NOT EXISTS [cron_id] ON [cron] ([job]);
