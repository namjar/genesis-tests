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

tablesDict = {          # for code on 162 string
    0:['countTables'],
    1:['blocks'],
    2:['contracts'],
    3:['history'],
    4:['keys'],
    5:['languages'],
    6:['members'],
    7:['menus'],
    8:['notifications'],
    9:['pages'],
    10:['parameters'],
    11:['roles_assign'],
    12:['roles_list'],
    13:['sections'],
    14:['signatures'],
    15:['tables']
}

def getCountDBObjects(dbParams):
    connect = psycopg2.connect(host=dbParams['dbHost'],
                               port=dbParams['dbPort'],
                               dbname=dbParams['dbName'],
                               user=dbParams['login'],
                               password=dbParams['password'])

    cursor = connect.cursor()

    result = {}

    cursor.execute("select count(*) from INFORMATION_SCHEMA.TABLES WHERE table_schema='public'")
    countTables = cursor.fetchall()
    result["countTables"] = countTables[0][0]

    cursor.execute("SELECT count(*) FROM \"1_blocks\"")
    blocks = cursor.fetchall()
    result["blocks"] = blocks[0][0]

    cursor.execute("SELECT count(*) FROM \"1_contracts\"")
    contracts = cursor.fetchall()
    result["contracts"] = contracts[0][0]

    cursor.execute("SELECT count(*) FROM \"1_history\"")
    history = cursor.fetchall()
    result["history"] = history[0][0]

    cursor.execute("SELECT count(*) FROM \"1_keys\"")
    keys = cursor.fetchall()
    result["keys"] = keys[0][0]

    cursor.execute("SELECT count(*) FROM \"1_languages\"")
    languages = cursor.fetchall()
    result["languages"] = languages[0][0]

    cursor.execute("SELECT count(*) FROM \"1_members\"")
    members = cursor.fetchall()
    result["members"] = members[0][0]

    cursor.execute("SELECT count(*) FROM \"1_menu\"")
    menus = cursor.fetchall()
    result["menus"] = menus[0][0]

    cursor.execute("SELECT count(*) FROM \"1_notifications\"")
    notifications = cursor.fetchall()
    result["notifications"] = notifications[0][0]

    cursor.execute("SELECT count(*) FROM \"1_pages\"")
    pages = cursor.fetchall()
    result["pages"] = pages[0][0]

    cursor.execute("SELECT count(*) FROM \"1_parameters\"")
    parameters = cursor.fetchall()
    result["parameters"] = parameters[0][0]

    cursor.execute("SELECT count(*) FROM \"1_roles_assign\"")
    roles_assign = cursor.fetchall()
    result["roles_assign"] = roles_assign[0][0]

    cursor.execute("SELECT count(*) FROM \"1_roles_list\"")
    roles_list = cursor.fetchall()
    result["roles_list"] = roles_list[0][0]

    cursor.execute("SELECT count(*) FROM \"1_sections\"")
    sections = cursor.fetchall()
    result["sections"] = sections[0][0]

    cursor.execute("SELECT count(*) FROM \"1_signatures\"")
    signatures = cursor.fetchall()
    result["signatures"] = signatures[0][0]

    cursor.execute("SELECT count(*) FROM \"1_tables\"")
    tables = cursor.fetchall()
    result["tables"] = tables[0][0]

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
                print("*** ERROR: CountDBObjects: "+ str(args.dbName) + str(i+1) + " != " + str(args.dbName) + str(j+1))

                # verification items of responses
                k = 0
                while k<len(tablesDict):
                    key = str(tablesDict[k])
                    key = key.replace("[","")
                    key = key.replace("]", "")
                    key = key.replace("'", "")
                    if res[i][key] != res[j][key]:
                        print("Not Equals: " + str(tablesDict[k]) +": " + str(res[i][key]) + " != " + str(res[j][key]))
                    k = k + 1

                #print(res[i])
                #print(res[j])
            else:
                if logAll == 1:
                    if i != j:
                        print("OK: " + str(args.dbName) + str(i+1) + " = " + str(args.dbName)+ str(j+1))
            j = j + 1
        i = i + 1
    print("----------------------------------------------------------------------------------------")



# Start script
print("Start monitoring...")
i = 0
while i<timeout:
    res = getAllDBResponses(dbParams)
    '''
    # error responses for test
    res[1]['languages'] = 500     
    res[1]['pages'] = 300
    res[0]['menus'] = 300
    '''
    verifyAllDBResponses(res)
    time.sleep(timeout)

