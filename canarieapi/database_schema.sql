CREATE TABLE [stats] (
  [route] VARCHAR(32),
  [invocations] INTEGER,
  [last_access] DATETIME);

CREATE UNIQUE INDEX [route_id] ON [stats] ([route]);