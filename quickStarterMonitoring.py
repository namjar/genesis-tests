from datetime import datetime
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
tablesList = []             # list of table names


def getCountDBObjects(dbParams):
    connect = psycopg2.connect(host=dbParams['dbHost'],
                               port=dbParams['dbPort'],
                               dbname=dbParams['dbName'],
                               user=dbParams['login'],
                               password=dbParams['password'])

    global tablesList
    tablesList.clear()

    cursor = connect.cursor()
    result = {}

    cursor.execute("select count(*) from INFORMATION_SCHEMA.TABLES WHERE table_schema='public'")
    countTables = cursor.fetchall()
    result["countTables"] = countTables[0][0]
    tablesList.append('countTables')

    cursor.execute("SELECT count(*) FROM \"1_blocks\"")
    blocks = cursor.fetchall()
    result["blocks"] = blocks[0][0]
    tablesList.append('blocks')

    cursor.execute("SELECT count(*) FROM \"1_contracts\"")
    contracts = cursor.fetchall()
    result["contracts"] = contracts[0][0]
    tablesList.append('contracts')

    cursor.execute("SELECT count(*) FROM \"1_history\"")
    history = cursor.fetchall()
    result["history"] = history[0][0]
    tablesList.append('history')

    cursor.execute("SELECT count(*) FROM \"1_keys\"")
    keys = cursor.fetchall()
    result["keys"] = keys[0][0]
    tablesList.append('keys')

    cursor.execute("SELECT count(*) FROM \"1_languages\"")
    languages = cursor.fetchall()
    result["languages"] = languages[0][0]
    tablesList.append('languages')

    cursor.execute("SELECT count(*) FROM \"1_members\"")
    members = cursor.fetchall()
    result["members"] = members[0][0]
    tablesList.append('members')

    cursor.execute("SELECT count(*) FROM \"1_menu\"")
    menus = cursor.fetchall()
    result["menus"] = menus[0][0]
    tablesList.append('menus')

    cursor.execute("SELECT count(*) FROM \"1_notifications\"")
    notifications = cursor.fetchall()
    result["notifications"] = notifications[0][0]
    tablesList.append('notifications')

    cursor.execute("SELECT count(*) FROM \"1_pages\"")
    pages = cursor.fetchall()
    result["pages"] = pages[0][0]
    tablesList.append('pages')

    cursor.execute("SELECT count(*) FROM \"1_parameters\"")
    parameters = cursor.fetchall()
    result["parameters"] = parameters[0][0]
    tablesList.append('parameters')

    cursor.execute("SELECT count(*) FROM \"1_roles_assign\"")
    roles_assign = cursor.fetchall()
    result["roles_assign"] = roles_assign[0][0]
    tablesList.append('roles_assign')

    cursor.execute("SELECT count(*) FROM \"1_roles_list\"")
    roles_list = cursor.fetchall()
    result["roles_list"] = roles_list[0][0]
    tablesList.append('roles_list')

    cursor.execute("SELECT count(*) FROM \"1_sections\"")
    sections = cursor.fetchall()
    result["sections"] = sections[0][0]
    tablesList.append('sections')

    cursor.execute("SELECT count(*) FROM \"1_signatures\"")
    signatures = cursor.fetchall()
    result["signatures"] = signatures[0][0]
    tablesList.append('signatures')

    cursor.execute("SELECT count(*) FROM \"1_tables\"")
    tables = cursor.fetchall()
    result["tables"] = tables[0][0]
    tablesList.append('tables')

    cursor.execute("SELECT count(*) FROM \"block_chain\"")
    block_chain = cursor.fetchall()
    result["block_chain"] = block_chain[0][0]
    tablesList.append('block_chain')

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
    print("------------------------------------------------")
    print(str(datetime.now()) + "\n")
    res = responses
    i = 0
    while i < len(res)-1:
        j = i + 1
        while j < len(res):
            if res[i] != res[j]:
                for index in range(len(tablesList)):
                    key = tablesList[index]

                    if (res[i][key] != res[j][key]) & (key == "block_chain"):
                        delta = abs(res[i][key] - res[j][key])
                        if delta>5:
                            print("ERROR: CountDBObjects: " + str(args.dbName) + str(i + 1) + " != " + str(args.dbName) + str(j + 1))
                            print(" Not Equals: " + str(tablesList[index]) + ": " + str(res[i][key]) + " != " + str(res[j][key]))
                        else:
                            if logAll == 1:
                                if i != j:
                                    print("OK: " + str(args.dbName) + str(i + 1) + " = " + str(args.dbName) + str(j + 1))
                                    print(" " + str(tablesList[index]) + ": " + str(res[i][key]) + " != " + str(res[j][key]))

                    if (res[i][key] != res[j][key]) & (key != "block_chain"):
                            print("ERROR: CountDBObjects: " + str(args.dbName) + str(i + 1) + " != " + str(args.dbName) + str(j + 1))
                            print(" Not Equals: " + str(tablesList[index]) + ": " + str(res[i][key]) + " != " + str(res[j][key]))

            else:
                if logAll == 1:
                    if i != j:
                        print("OK: " + str(args.dbName) + str(i + 1) + " = " + str(args.dbName) + str(j + 1))

            #print("")
            #print(res[i])
            #print(res[j])

            j = j + 1
        i = i + 1


# Start script
print("Start monitoring...")
print("Nodes count = " + str(nodesCount))
while True:
    res = getAllDBResponses(dbParams)
    '''
    # error responses for test
    res[1]['languages'] = 500     
    res[1]['pages'] = 300
    res[0]['menus'] = 300
    '''
    verifyAllDBResponses(res)
    time.sleep(timeout)

