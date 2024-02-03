import mysql.connector
def reconnect_mysql():
    cnx = None
    try:
        cnx = mysql.connector.connect(
            host="host",
            user="user",
            password="password",
            database="database"
        )
        if cnx.is_connected():
            print('ok')
    except Error as e:
        print(f'errer:{e:}')
    return cnx
    

channel_access_token = r'channel_access_token'

channel_secret =  r'channel_secret'

access_token = r'access_token' 
