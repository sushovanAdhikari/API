import psycopg2
import json
import os

def db_connect():

    # get db connection from json
    cred_json_file = 'db_credentials.json'
    path = os.getcwd()
    cred_file_path = os.path.join(path, cred_json_file)
    with open(cred_file_path, 'r') as file:
        cred = json.load(file)
        
    conn = psycopg2.connect(
        host=cred["host"],
        database=cred["database"],
        user=cred["user"],
        password=cred["password"]
    )
    return conn

def stored_procedure_call(connection, routine_type, routine_name, *args):

    sql_command = ''

    if routine_name == '' or routine_name == None:
        raise ValueError('Stored Procedure or Functiona Name is required.')

    if routine_type == 'STORED-PROCEDURE':
        sql_command = 'Call'
    elif routine_type == 'FUNCTION':
        sql_command = 'Select'
    else:
        raise ValueError('Incorrect routine_name received. routine-name should be either STORED-PROCEDURE or FUNCTION')
    
    with connection.cursor() as cur:
        placeholders = ', '.join(['%s'] * len(args))
        query = f"{sql_command} {routine_name}({placeholders})"
        cur.execute(query, args)
        connection.commit()
