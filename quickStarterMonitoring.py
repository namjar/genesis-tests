import time
import psycopg2
import argparse

'''
Examles for start

python quickStarterMonitoring.py -dbHost=localhost -dbPort=5430 -dbName=genesis -dbUser=postgres -dbPassword=postgres -nodesCount=4 -timeout=5 -logAll=1

python quickStarterMonitoring.py -nodesCount=4
'''


parser = argparse.ArgumentParser()
parser.add_argument('-dbHost', default='localhost')
parser.add_argument('-dbPort', default='5430')
parser.add_argument('-dbName', default='genesis')
parser.add_argument('-dbUser', default='postgres')
parser.add_argument('-dbPassword', default='postgres')

parser.add_argument('-logAll', default='1')         # print Errors and Ok. If logAll=0 print only Errors
parser.add_argument('-nodesCount', default='2')
parser.add_argument('-timeout', default='2')        # check every 'timeout' seconds
args = parser.parse_args()

dbParams = {
    "dbHost": args.dbHost,
    'dbPort' : args.dbPort,
    'dbName' : args.dbName,
    'login' : args.dbUser,
    'password' : args.dbPassword
}

logAll = int(args.logAll)
nodesCount = int(args.nodesCount)
timeout = int(args.timeout)

'''
dbParams = {
    "dbHost": "localhost",
    'dbPort' : '5430',
    'dbName' : 'genesis',
    'login' : 'postgres',
    'password' : 'postgres'
}
'''


def getCountDBObjects(dbParams):
	connect = psycopg2.connect(host=dbParams['dbHost'],
                               port=dbParams['dbPort'],
                               dbname=dbParams['dbName'],
                               user=dbParams['login'],
                               password=dbParams['password'])
	cursor = connect.cursor()
	cursor.execute("select count(*) from INFORMATION_SCHEMA.TABLES WHERE table_schema='public'")
	tables = cursor.fetchall()
	cursor.execute("SELECT count(*) FROM \"1_contracts\"")
	contracts = cursor.fetchall()
	cursor.execute("SELECT count(*) FROM \"1_pages\"")
	pages = cursor.fetchall()
	cursor.execute("SELECT count(*) FROM \"1_menu\"")
	menus = cursor.fetchall()
	cursor.execute("SELECT count(*) FROM \"1_blocks\"")
	blocks = cursor.fetchall()
	cursor.execute("SELECT count(*) FROM \"1_parameters\"")
	params = cursor.fetchall()
	cursor.execute("SELECT count(*) FROM \"1_languages\"")
	locals = cursor.fetchall()

	result = {}
	result["tables"] = tables[0][0]
	result["contracts"] = contracts[0][0]
	result["pages"] = pages[0][0]
	result["menus"] = menus[0][0]
	result["blocks"] = blocks[0][0]
	result["params"] = params[0][0]
	result["locals"] = locals[0][0]


	return result


def getAllDBResponses(dbParams):
    responsesArray = []
    i = 0
    while i<nodesCount:
        dbname = ""
        dbname = "genesis" + str(i+1)
        dbParams['dbName'] = dbname
        responsesArray.append(getCountDBObjects(dbParams))
        i = i + 1
    return responsesArray


def printAllDBResponses(responses):
    i = 0
    while i < nodesCount:
        print(responses[i])
        i = i + 1

def verifyAllDBResponses(responses):
    res = responses
    i = 0
    while i < len(res)-1:
        j = i + 1
        while j < len(res):
            if res[i] != res[j]:
                print("ERROR: CountDBObjects: "+"genesis" + str(i+1)+ " != genesis" + str(j+1))
                print(res[i])
                print(res[j])
            else:
                if logAll == 1:
                    if i != j:
                        print("OK: " + "genesis" + str(i+1)+ " = genesis" + str(j+1))
            j = j + 1
        i = i + 1



# Start script
print("Start monitoring...")
i = 0
while i<timeout:
    res = getAllDBResponses(dbParams)
    #res[1]['locals'] = 500     # error response for test
    verifyAllDBResponses(res)
    print("---------------------------------------------")
    time.sleep(timeout)

