CREATE TABLE [stats] (
  [route] VARCHAR(32),
  [invocations] INTEGER,
  [last_access] DATETIME);

CREATE UNIQUE INDEX [stats_id] ON [stats] ([route]);

CREATE TABLE [status] (
  [route] VARCHAR(32),
  [service] VARCHAR(32),
  [status] VARCHAR(8),
  [message] VARCHAR(256));

CREATE UNIQUE INDEX [status_id] ON [status] ([route], [service]);

CREATE TABLE [cron] (
  [job] VARCHAR(32),
  [last_execution] DATETIME);

CREATE UNIQUE INDEX [cron_id] ON [cron] ([job]);
