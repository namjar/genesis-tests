import unittest
import utils
import config
import requests
import json
import time
import funcs


class ContractFunctionsTestCase(unittest.TestCase):
    def setUp(self):
        self.config = config.getNodeConfig()
        global url, prKey,token, dbHost, dbName, login, pas
        self.contracts = config.readFixtures("contracts")
        url = self.config["2"]["url"]
        prKey = self.config["1"]['private_key']
        dbHost = self.config["1"]["dbHost"]
        dbName = self.config["1"]['dbName']
        login = self.config["1"]["login"]
        pas = self.config["1"]['pass']
        self.data = utils.login(url,prKey, 0)
        token = self.data["jwtToken"]

    def assertTxInBlock(self, result, jwtToken):
        self.assertIn("hash",  result)
        status = utils.txstatus(url,
                                self.config["1"]["time_wait_tx_in_block"],
                                result['hash'], jwtToken)
        print(status)
        self.assertNotIn(json.dumps(status), 'errmsg')
        self.assertGreater(len(status['blockid']), 0)

    def generate_name_and_code(self, sourseCode):
        name = utils.generate_random_name()
        code = "contract " + name + sourseCode
        return code, name

    def create_contract(self, code):
        data = {"Wallet": "", "ApplicationId": 1,
                "Value": code,
                "Conditions": "ContractConditions(\"MainCondition\")"}
        result = utils.call_contract(url, prKey, "NewContract",
                                     data, token)
        self.assertTxInBlock(result, token)

    def call_contract(self, name, data):
        result = utils.call_contract(url, prKey, name,
                                     data, token)
        self.assertTxInBlock(result, token)


    def check_contract(self, sourse, checkPoint):
        code, name = self.generate_name_and_code(sourse)
        self.create_contract(code)
        url = self.config["2"]["url"]
        prKey = self.config["1"]['private_key']
        token = self.data["jwtToken"]
        sleep = self.config["1"]["time_wait_tx_in_block"]
        res = utils.call_contract(url, prKey, name, {}, token)
        hash = res["hash"]
        result = utils.txstatus(url, sleep, hash, token)
        self.assertIn(checkPoint, result["result"], "error")

    def call(self, name, data):
        url = self.config["2"]["url"]
        prKey = self.config["1"]['private_key']
        token = self.data["jwtToken"]
        result = utils.call_contract(url, prKey, name, data, token)
        status = utils.txstatus(url,
                                self.config["1"]["time_wait_tx_in_block"],
                                result['hash'], token)
        return status
      
    def check_contract_with_data(self, sourse, data, checkPoint):
        code, name = self.generate_name_and_code(sourse)
        self.create_contract(code)
        url = self.config["2"]["url"]
        prKey = self.config["1"]['private_key']
        token = self.data["jwtToken"]
        sleep = self.config["1"]["time_wait_tx_in_block"]
        res = utils.call_contract(url, prKey, name, data, token)
        hash = res["hash"]
        result = utils.txstatus(url, sleep, hash, token)
        self.assertIn(checkPoint, result["result"], "error")

    def test_contract_dbfind(self):
        contract = self.contracts["dbFind"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_ecosysParam(self):
        contract = self.contracts["ecosysParam"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_dbRow(self):
        contract = self.contracts["dbRow"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_ifMap(self):
        contract = self.contracts["ifMap"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_evalCondition(self):
        contract = self.contracts["evalCondition"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_validateCondition(self):
        contract = self.contracts["validateCondition"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_addressToId(self):
        contract = self.contracts["addressToId"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_contract_one(self):
        contract = self.contracts["one"]
        self.check_contract(contract["code"], contract["asert"])
    
    def test_contract_row(self):
        contract = self.contracts["row"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_contains(self):
        contract = self.contracts["contains"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_float(self):
        contract = self.contracts["float"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_hasPrefix(self):
        contract = self.contracts["hasPrefix"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_hexToBytes(self):
        contract = self.contracts["hexToBytes"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_Int(self):
        contract = self.contracts["int"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_len(self):
        contract = self.contracts["len"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_pubToID(self):
        contract = self.contracts["pubToID"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_replace(self):
        contract = self.contracts["replace"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_size(self):
        contract = self.contracts["size"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_contract_blockTime(self):
        contract = self.contracts["blockTime"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_sha256(self):
        contract = self.contracts["sha256"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_Sprintf(self):
        contract = self.contracts["sprintf"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_contract_elseif(self):
        contract = self.contracts["elseif"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_contract_toUpper(self):
        contract = self.contracts["toUpper"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_str(self):
        contract = self.contracts["str"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_substr(self):
        contract = self.contracts["substr"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_sysParamString(self):
        contract = self.contracts["sysParamString"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_sysParamInt(self):
        contract = self.contracts["updSysParam"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_updSysParam(self):
        contract = self.contracts["updSysParam"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_getContractById(self):
        contract = self.contracts["getContractById"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_getContractByName(self):
        contract = self.contracts["getContractByName"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_random(self):
        contract = self.contracts["random"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_contract_langRes(self):
        data = {"ApplicationId":1,
                "Name": "test",
                "Trans": "{\"en\": \"test_en\", \"de\" : \"test_de\"}"}
        result = utils.call_contract(url, prKey, "NewLang", data, token)
        tx = utils.txstatus(url, self.config["1"]["time_wait_tx_in_block"], result['hash'], token)
        contract = self.contracts["langRes"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_contract_dbInsert(self):
        columns = """[{"name":"name","type":"varchar",
        "index": "1",  "conditions":"true"},
        {"name":"test","type":"varchar",
        "index": "0",  "conditions":"true"}]"""
        permission = """{"insert": "true",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "test", "ApplicationId":1,
                "Columns": columns,
                "Permissions": permission}
        result = utils.call_contract(url, prKey, "NewTable", data, token)
        tx = utils.txstatus(url,
                                self.config["1"]["time_wait_tx_in_block"],
                                result['hash'], token)
        contract = self.contracts["dbInsert"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_contract_dbUpdate(self):        
        columns = """[{"name":"name","type":"varchar",
        "index": "1",  "conditions":"true"},
        {"name":"test","type":"varchar",
        "index": "0",  "conditions":"true"}]"""
        permission = """{"insert": "true",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "test", "ApplicationId":1,
                "Columns": columns,
                "Permissions": permission}
        result = utils.call_contract(url, prKey, "NewTable", data, token)
        tx = utils.txstatus(url,
                                self.config["1"]["time_wait_tx_in_block"],
                                result['hash'], token)
        contract = self.contracts["dbInsert"]
        self.check_contract(contract["code"], contract["asert"])
        contract = self.contracts["dbUpdate"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_contract_idToAddress(self):
        contract = self.contracts["idToAddress"]
        self.check_contract(contract["code"], contract["asert"])    
        
    def test_contract_join(self):
        contract = self.contracts["join"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_contract_split(self):
        contract = self.contracts["split"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_contracts_dbUpdateExt(self):
        columns = """[{"name":"name","type":"varchar",
        "index": "1",  "conditions":"true"},
        {"name":"test","type":"varchar",
        "index": "0",  "conditions":"true"}]"""
        permission = """{"insert": "true",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "test", "ApplicationId":1,
                "Columns": columns,
                "Permissions": permission}
        result = utils.call_contract(url, prKey, "NewTable", data, token)
        tx = utils.txstatus(url,
                                self.config["1"]["time_wait_tx_in_block"],
                                result['hash'], token)
        contract = self.contracts["dbInsert"]
        self.check_contract(contract["code"], contract["asert"])
        contract = self.contracts["dbUpdateExt"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_contract_callContract(self):
        contract = self.contracts["myContract"]
        code = "contract MyContract" + contract["code"]
        data = {"Value": code, "ApplicationId": 1, "Conditions": "true"}
        res = utils.call_contract(url, prKey, "NewContract", data, token)
        time.sleep(10)
        contract = self.contracts["callContract"]
        self.check_contract(contract["code"], contract["asert"])
    
    def test_type_bool(self):
        contract = self.contracts["type_bool"]
        self.check_contract(contract["code"], contract["asert"])

    def test_type_bytes(self):
        contract = self.contracts["type_bytes"]
        self.check_contract(contract["code"], contract["asert"])

    def test_type_int(self):
        contract = self.contracts["type_int"]
        self.check_contract(contract["code"], contract["asert"])

    def test_type_address(self):
        contract = self.contracts["type_address"]
        self.check_contract(contract["code"], contract["asert"])

    def test_type_array(self):
        contract = self.contracts["type_array"]
        self.check_contract(contract["code"], contract["asert"])

    def test_type_map(self):
        contract = self.contracts["type_map"]
        self.check_contract(contract["code"], contract["asert"])

    def test_type_money(self):
        contract = self.contracts["type_money"]
        self.check_contract(contract["code"], contract["asert"])

    def test_type_float(self):
        contract = self.contracts["type_float"]
        self.check_contract(contract["code"], contract["asert"])

    def test_type_string(self):
        contract = self.contracts["type_string"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_getBlock(self):
        contract = self.contracts["getBlock"]
        self.check_contract(contract["code"], contract["asert"])


    def test_getColumnType(self):
        contract = self.contracts["getColumnType"]
        self.check_contract(contract["code"], contract["asert"])
      
    def test_decodeBase64(self):
        contract = self.contracts["decodeBase64"]
        self.check_contract(contract["code"], contract["asert"])

    def test_encodeBase64(self):
        contract = self.contracts["encodeBase64"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_jsonEncode(self):
        contract = self.contracts["jsonEncode"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_jsonDecode(self):
        contract = self.contracts["jsonDecode"]
        self.check_contract(contract["code"], contract["asert"])

    def test_sys_var_role_id(self):
        contract = self.contracts["sys_var_roleID"]
        self.check_contract(contract["code"], contract["asert"])

    def test_sys_var_role_id_readonly(self):
        sysVarName = "$role_id"
        contracName = utils.generate_random_name()
        value = "contract con_" + contracName + " { data{ } conditions{ } action{ "+ sysVarName + " = 5 } }"
        data = {"Value": value, "ApplicationId": 1, "Conditions": "true"}
        result = utils.call_contract(url, prKey, "NewContract", data, token)
        tx = utils.txstatus(url,
                            self.config["1"]["time_wait_tx_in_block"],
                            result['hash'], token)
        expResult = "system variable "+sysVarName+" cannot be changed"
        msg = "system variable "+sysVarName+" was been changed!"
        self.assertEqual(tx["errmsg"]["error"], expResult, msg)

    def test_bytesToString(self):
        contract = self.contracts["bytesToString"]
        self.check_contract(contract["code"], contract["asert"])

    def test_stringToBytes(self):
        contract = self.contracts["stringToBytes"]
        self.check_contract(contract["code"], contract["asert"])

    def getMetrics(self, ecosystemNum, metricName):
        # get metrics count
        res = funcs.get_list(url, "metrics", token)
        i = 0
        while i < len(res['list']):
            if (int(res['list'][i]['key']) == int(ecosystemNum)) and (str(res['list'][i]['metric']) == str(metricName)):
                return res['list'][i]['value']
            i += 1

    def test_z1_dbSelectMetricsMin(self):
        # func generate contract which return block_id and increment count blocks
        def waitBlockId(old_block_id, limit):
            while True:
                if old_block_id == limit:
                    break
                contracName = utils.generate_random_name()
                value = "contract con_" + contracName + " {\n data{} \n conditions{} \n action { \n  $result = $block \n } \n }"
                data = {"Value": value, "ApplicationId": 1, "Conditions": "true"}
                result = utils.call_contract(url, prKey, "NewContract", data, token)
                tx = utils.txstatus(url,
                                    self.config["1"]["time_wait_tx_in_block"],
                                    result['hash'], token)
                current_block_id = int(tx["blockid"])
                self.assertGreater(current_block_id, 0, "BlockId is not generated: " + str(tx))
                old_block_id = current_block_id

        # generate contract which return count blocks in blockchain
        contracName = utils.generate_random_name()
        value = "contract con_" + contracName + " {\n data{} \n conditions{} \n action { \n  $result = $block \n } \n }"
        data = {"Value": value, "ApplicationId": 1, "Conditions": "true"}
        result = utils.call_contract(url, prKey, "NewContract", data, token)
        tx = utils.txstatus(url,
                            self.config["1"]["time_wait_tx_in_block"],
                            result['hash'], token)
        current_block_id = int(tx["blockid"])
        self.assertGreater(current_block_id, 0, "BlockId is not generated: " + str(tx))
        # wait until generated 100 blocks
        if current_block_id < 100:
            waitBlockId(current_block_id, 100)
        # wait until generated multiples of 100 blocks
        if (current_block_id % 100 >= 90):
            count = current_block_id + (100 - (current_block_id % 100))
            waitBlockId(current_block_id, count)
        # test
        ecosystem_tx = self.getMetrics(1, "ecosystem_tx")
        contract = self.contracts["dbSelectMetricsMin"]
        self.check_contract(contract["code"], str(ecosystem_tx))

    def test_z2_dbSelectMetricsMax(self):
        # Run test after test_z1_dbSelectMetricsMin
        ecosystem_members = self.getMetrics(1, "ecosystem_members")
        contract = self.contracts["dbSelectMetricsMax"]
        self.check_contract(contract["code"], str(ecosystem_members))

    def test_z3_dbSelectMetricsAvg(self):
        # Run test after test_z1_dbSelectMetricsMin
        ecosystem_pages = self.getMetrics(1,"ecosystem_pages")
        contract = self.contracts["dbSelectMetricsAvg"]
        self.check_contract(contract["code"], str(ecosystem_pages))
        
    def test_getMapKeys(self):
        contract = self.contracts["getMapKeys"]
        self.check_contract(contract["code"], contract["asert"])

    def test_sortedKeys(self):
        contract = self.contracts["sortedKeys"]
        self.check_contract(contract["code"], contract["asert"])
        
    def test_getHistoryContract(self):
        # create contract
        replacedString = "old_var"
        code = """
        { 
            data{}
            conditions{}
            action{ var %s int }
        }
        """ %replacedString
        code, name = self.generate_name_and_code(code)
        self.create_contract(code)
        # change contract
        id = funcs.get_object_id(url, name, "contracts", token)
        newCode = code.replace(replacedString, "new_var")
        data = {"Id": id,
                "Value": newCode}
        self.call_contract("EditContract", data)
        # test
        data = {"Table": "contracts", "ID": id}
        contract = self.contracts["getHistory"]
        self.check_contract_with_data(contract["code"], data, replacedString)

    def test_getHistoryPage(self):
        # create page
        name = utils.generate_random_name()
        page = "Div(Body: Hello)"
        data = {"ApplicationId": "1",
                "Name": name,
                "Value": page,
                "Menu": "default_menu",
                "Conditions": "true"}
        self.call_contract("NewPage", data)
        # change page
        id = funcs.get_object_id(url, name, "pages", token)
        newValuePage = page.replace("Hello", "new_var")
        data = {"Id": id,
                "Value": newValuePage}
        self.call_contract("EditPage", data)
        # test
        data = {"Table": "pages", "ID": id}
        contract = self.contracts["getHistory"]
        self.check_contract_with_data(contract["code"], data, page)

    def test_append(self):
        contract = self.contracts["append"]
        self.check_contract(contract["code"], contract["asert"])

    def test_sys_var_stack(self):
        # This test has not a fixture
        innerBody = """
                {
                data{}
                conditions{}
                action {
                    $result = $stack
                    }
                }
                """
        innerCode, innerName = self.generate_name_and_code(innerBody)
        self.create_contract(innerCode)
        outerBody = """
                {
                data{}
                conditions{}
                action {
                    var par map
                    var res string
                    res = CallContract("%s", par)
                    $result = res
                    }
                }
                """ % innerName
        outerCode, outerName = self.generate_name_and_code(outerBody)
        self.create_contract(outerCode)
        data = {"Wallet": "", "ApplicationId": 1,
                "Value": outerCode,
                "Conditions": "ContractConditions(\"MainCondition\")"}
        res = self.call(outerName, data)
        mustBe = "[@1" + outerName + " CallContract @1" + innerName +"]"
        self.assertEqual(mustBe, res["result"], "test_sys_var_stack is failed!")

    def test_getHistoryRowMenu(self):
        # create menu
        rollc_before = utils.getMaxIdFromTable(dbHost, dbName, login, pas, "rollback_tx")
        name = utils.generate_random_name()
        menu = "This is new menu"
        data = {"Name": name,
                "Value": menu,
                "Conditions": "true"}
        self.call_contract("NewMenu", data)
        rollc_after = utils.getMaxIdFromTable(dbHost, dbName, login, pas, "rollback_tx")
        # change menu
        id = funcs.get_object_id(url, name, "menu", token)
        newValueMenu = menu.replace("new menu", "new_var")
        data = {"Id": id,
                "Value": newValueMenu}
        self.call_contract("EditMenu", data)
        # test
        query = """SELECT id FROM "rollback_tx" WHERE table_name = '1_menu' AND data='' AND id >= %s AND id <= %s""" % (
            rollc_before, rollc_after)
        rollback_id = utils.executeSQL(dbHost, dbName, login, pas, query)[0][0]
        data = {"Table": "menu", "ID": id, "rID": rollback_id}
        contract = self.contracts["getHistoryRow"]
        self.check_contract_with_data(contract["code"], data, menu)

    def test_getHistoryRowBlock(self):
        # create block
        rollc_before = utils.getMaxIdFromTable(dbHost, dbName, login, pas, "rollback_tx")
        name = utils.generate_random_name()
        block = "Div(Body: Hello)"
        data = {"ApplicationId": "1",
                "Name": name,
                "Value": block,
                "Conditions": "true"}
        self.call_contract("NewBlock", data)
        rollc_after = utils.getMaxIdFromTable(dbHost, dbName, login, pas, "rollback_tx")
        # change block
        id = funcs.get_object_id(url, name, "blocks", token)
        newValueBlock = block.replace("Hello", "new_var")
        data = {"Id": id,
                "Value": newValueBlock}
        self.call_contract("EditBlock", data)
        # test
        query = """SELECT id FROM "rollback_tx" WHERE table_name = '1_blocks' AND data='' AND id >= %s AND id <= %s""" % (
            rollc_before, rollc_after)
        rollback_id = utils.executeSQL(dbHost, dbName, login, pas, query)[0][0]
        data = {"Table": "blocks", "ID": id, "rID": rollback_id}
        contract = self.contracts["getHistoryRow"]
        self.check_contract_with_data(contract["code"], data, block)

if __name__ == '__main__':
    unittest.main()
