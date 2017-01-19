import pymssql

server = ''
database = ''
username = ''
password = ''

conn = pymssql.connect(server=server, user=username, password=password, database='conferences')
cursor = conn.cursor()
