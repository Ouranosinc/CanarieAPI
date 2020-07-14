import os
import psycopg2
import argparse
import sqlite3

def migrate(db_schema_root,sqllite_db_path,pg_conn_str,recreate_postgress_db):

    pg_conn = psycopg2.connect(pg_conn_str)

    if (recreate_postgress_db):
        with open(db_schema_root + "drop_all.sql", mode='r') as f:
            pg_execute_schema(pg_conn,f.read())

    # Create postgress DB
    with open(db_schema_root+"database_schema.sql", mode='r') as f:
        pg_execute_schema(pg_conn, f.read())

    # COPY everything from sqllite
    sqllite_conn=sqlite3.connect(sqllite_db_path)
    copytable(pg_conn, sqllite_conn, "status", "route, service, status, message")
    copytable(pg_conn, sqllite_conn, "stats", "route, invocations, last_access")
    copytable(pg_conn, sqllite_conn, "cron", "job, last_execution")

    sqllite_conn.close()

def pg_execute_schema(pg_conn,schema):
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute(schema)
    pg_conn.commit()


def copytable(pg_conn,sqllite_conn,tablename,fields: str):
    sqllite_query = f'select {fields} from {tablename}'
    sqllite_cur = sqllite_conn.cursor()
    res = sqllite_cur.execute(sqllite_query)
    pg_query=f'INSERT INTO {tablename} ({fields}) VALUES (' + ("%s,"*len(fields.split(","))).strip(',') + ');'
    pg_cursor= pg_conn.cursor()
    for item in res:
        pg_cursor.execute(pg_query,item)
    pg_conn.commit()
    sqllite_cur.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to migrate SQLlite to Posgres. From v 0.4.3 to v 0.5.0")
    parser.add_argument("--db_schema_path",help = "Path to the postgress schema file. If not supplied ../",default=" ../")
    parser.add_argument("--recreate_postgress_db",help="If True, it will drop all Postgres tables and recreate the database. Default false", default=False)
    parser.add_argument("sqllite_db_path",help="SQLlite database path")
    parser.add_argument("pg_conn_string",help= "Connections string to the postgres database")
    parser.print_help()
    args = parser.parse_args()
    print(args)
    print(args.pg_conn_string)
    migrate(args.db_schema_path,args.sqllite_db_path,args.pg_conn_string,args.recreate_postgress_db)
    #migrate("../","/opt/local/src/CanarieAPI/stats.db","dbname=%s user=%s password=%s host=%s port=%s" % ("postgres","postgres","login1","127.0.0.1","5432"))