import unittest
import utils
import config
import requests
import json
import funcs
import os
import time


class SystemContractsTestCase(unittest.TestCase):
    
    def setUp(self):
        global url, token, prKey, pause, dbHost, dbName, login, pas
        self.config = config.getNodeConfig()
        url = self.config["1"]["url"]
        pause = self.config["1"]["time_wait_tx_in_block"]
        prKey = self.config["1"]['private_key']
        dbHost = self.config["1"]["dbHost"]
        dbName = self.config["1"]['dbName']
        login = self.config["1"]["login"]
        pas = self.config["1"]['pass']
        self.data = utils.login(url, prKey, 0)
        token = self.data["jwtToken"]            
        
    def call(self, name, data):
        resp = utils.call_contract(url, prKey, name, data, token)
        print(resp)
        resp = utils.getTxStatus(url, pause, resp, token)
        return resp
    
    def waitBlockId(self, old_block_id, limit):
        while True:
            # add contract, which get block_id
            body = "{\n data{} \n conditions{} \n action { \n  $result = $block \n } \n }"
            code, name = utils.generate_name_and_code(body)
            data = {"Value": code, "ApplicationId": 1,
                    "Conditions": "true"}
            res = self.call("NewContract", data)
            self.assertGreater(res["blockid"], 0, "BlockId is not generated: " + str(res))
            currrent_block_id = res["blockid"]
            expected_block_id = old_block_id + limit + 1 # +1 spare block
            if currrent_block_id == expected_block_id:
                break
            
    def test_create_ecosystem(self):
        name = "Ecosys_" + utils.generate_random_name()
        data = {"Name": name}
        res = self.call("NewEcosystem", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        
    def test_edit_application(self):
        name = "App" + utils.generate_random_name()
        data = {"Name": name, "Conditions": "true"}
        res = self.call("NewApplication", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        id = funcs.get_application_id(url, name, token)
        data = {"ApplicationId": id, "Conditions": "false"}
        res = self.call("EditApplication", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        
    def test_activate_application(self):
        name = "App" + utils.generate_random_name()
        data = {"Name": name, "Conditions": "true"}
        res = self.call("NewApplication", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        id = funcs.get_application_id(url, name, token)
        dataDeact = {"ApplicationId": id, "Value": 0}
        res = self.call("DelApplication", dataDeact)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataAct = {"ApplicationId": id, "Value": 1}
        res = self.call("DelApplication", dataAct)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        
    def test_export_application(self):
        name = "App" + utils.generate_random_name()
        data = {"Name": name, "Conditions": "true"}
        res = self.call("NewApplication", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        id = funcs.get_application_id(url, name, token)
        dataDeact = {"ApplicationId": id}
        res = self.call("ExportNewApp", dataDeact)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        
    def test_edit_ecosystem_name(self):
        id = 1
        newName = "Ecosys_"+utils.generate_random_name()
        data = {"EcosystemID": id, "NewName": newName}
        resBlockId = self.call("EditEcosystemName", data)
        self.assertGreater(resBlockId["blockid"], 0,
                           "BlockId is not generated: " + str(resBlockId))
        

    def test_edit_ecosystem_name_incorrect_id(self):
        id = 500
        newName = "ecosys_"+utils.generate_random_name()
        data = {"EcosystemID": id, "NewName": newName}
        res = self.call("EditEcosystemName", data)
        self.assertEqual("Ecosystem "+str(id)+" does not exist", res["error"])

    def test_money_transfer(self):
        data = {"Recipient": "0005-2070-2000-0006-0200", "Amount": "2999479990390000000"}
        res = self.call("MoneyTransfer", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_money_transfer_incorrect_wallet(self):
        wallet = "0005-2070-2000-0006"
        msg = "Recipient " + wallet + " is invalid"
        data = {"Recipient": wallet, "Amount": "1000"}
        ans = self.call("MoneyTransfer", data)
        self.assertEqual(ans["error"], msg, "Incorrect message" + msg)

    def test_money_transfer_zero_amount(self):
        wallet = "0005-2070-2000-0006-0200"
        msg = "Amount must be greater then zero"
        data = {"Recipient": wallet, "Amount": "0"}
        ans = self.call("MoneyTransfer", data)
        self.assertEqual(ans["error"], msg, "Incorrect message" + msg)

    def test_money_transfer_negative_amount(self):
        wallet = "0005-2070-2000-0006-0200"
        msg = "Amount must be greater then zero"
        data = {"Recipient": wallet, "Amount": "-1000"}
        ans = self.call("MoneyTransfer", data)
        self.assertEqual(ans["error"], msg, "Incorrect message" + msg)

    def test_money_transfer_amount_as_string(self):
        wallet = "0005-2070-2000-0006-0200"
        msg = "can't convert ttt to decimal"
        data = {"Recipient": wallet, "Amount": "ttt"}
        ans = self.call("MoneyTransfer", data)
        self.assertEqual(ans["error"], msg, "Incorrect message" + msg)

    def test_money_transfer_with_comment(self):
        wallet = "0005-2070-2000-0006-0200"
        data = {"Recipient": wallet, "Amount": "1000", "Comment": "Test"}
        res = self.call("MoneyTransfer", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_contract(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_contract_exists_name(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        ans = self.call("NewContract", data)
        msg = "Contract " + name + " already exists"
        self.assertEqual(ans["error"], msg, "Incorrect message: " + str(ans))

    def test_new_contract_without_name(self):
        code = "contract {data { }    conditions {    }    action {    }    }"
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        ans = self.call("NewContract", data)
        self.assertIn("must be the name", ans["error"],
                      "Incorrect message: " + str(ans))

    def test_new_contract_incorrect_condition(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "condition"}
        ans = self.call("NewContract", data)
        self.assertEqual("unknown identifier condition",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_contract_incorrect_condition(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data2 = {"Id": funcs.get_contract_id(url, name, token),
                 "Value": code, "Conditions": "tryam",
                 "WalletId": "0005-2070-2000-0006-0200"}
        ans = self.call("EditContract", data2)
        self.assertEqual("unknown identifier tryam",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_contract_incorrect_condition1(self):
        newWallet = "0005"
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data2 = {"Id": funcs.get_contract_id(url, name, token),
                 "Value": code, "Conditions": "true",
                 "WalletId": newWallet}
        ans = self.call("EditContract", data2)
        msg = "New contract owner " + newWallet + " is invalid"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_edit_contract(self):
        code, name = utils.generate_name_and_code("")
        newWallet = "0005-2070-2000-0006-0200"
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        

    def test_edit_name_of_contract(self):
        newWallet = "0005-2070-2000-0006-0200"
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        code1, name1 = utils.generate_name_and_code("")
        data2 = {"Id": funcs.get_contract_id(url, name, token),
                 "Value": code1, "Conditions": "true",
                 "WalletId": "0005-2070-2000-0006-0200"}
        ans = self.call("EditContract", data2)
        self.assertEqual("Contracts or functions names cannot be changed",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_incorrect_contract(self):
        code, name = utils.generate_name_and_code("")
        id = "9999"
        data2 = {"Id": id, "Value": code, "Conditions": "true",
                 "WalletId": "0005-2070-2000-0006-0200"}
        ans = self.call("EditContract", data2)
        self.assertEqual("Item " + id + " has not been found",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_activate_contract(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1, "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        id = funcs.get_contract_id(url, name, token)
        data2 = {"Id": id}
        res = self.call("ActivateContract", data2)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_activate_incorrect_contract(self):
        id = "9999"
        data = {"Id": id}
        ans = self.call("ActivateContract", data)
        msg = "Contract " + id + " does not exist"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_deactivate_contract(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1, "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        id = funcs.get_contract_id(url, name, token)
        data2 = {"Id": id}
        res = self.call("ActivateContract", data2)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        res = self.call("DeactivateContract", data2)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_deactivate_incorrect_contract(self):
        id = "9999"
        data = {"Id": id}
        ans = self.call("DeactivateContract", data)
        self.assertEqual("Contract " + id + " does not exist",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_new_parameter(self):
        name = "Par_" + utils.generate_random_name()
        data = {"Name": name, "Value": "test", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewParameter", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_parameter_exist_name(self):
        name = "Par_" + utils.generate_random_name()
        data = {"Name": name, "Value": "test", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewParameter", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        msg = "Parameter " + name + " already exists"
        ans = self.call("NewParameter", data)
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_parameter_incorrect_condition(self):
        condition = "tryam"
        name = "Par_" + utils.generate_random_name()
        data = {"Name": name, "Value": "test", "ApplicationId": 1,
                "Conditions": condition}
        ans = self.call("NewParameter", data)
        self.assertEqual("unknown identifier " + condition,
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_incorrect_parameter(self):
        id = "9999"
        data2 = {"Id": id, "Value": "test_edited", "Conditions": "true"}
        ans = self.call("EditParameter", data2)
        self.assertEqual("Item " + id + " has not been found",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_parameter_incorrect_condition(self):
        name = "Par_" + utils.generate_random_name()
        data = {"Name": name, "Value": "test", "Conditions": "true"}
        res = self.call("NewParameter", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        id = funcs.get_parameter_id(url, name, token)
        condition = "tryam"
        data2 = {"Id": id, "Value": "test_edited", "Conditions": condition}
        ans = self.call("EditParameter", data2)
        self.assertEqual("unknown identifier " + condition,
                         ans["error"], "Incorrect message: " + str(ans))

    def test_new_menu(self):
        countMenu = utils.getCountTable(dbHost, dbName, login, pas, "1_menu")
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewMenu", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        content = {'tree': [{'tag': 'text', 'text': 'Item1'}]}
        mContent = funcs.get_content(url, "menu", name, "", 1, token)
        self.assertEqual(mContent, content)

    def test_new_menu_exist_name(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewMenu", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        ans = self.call("NewMenu", data)
        self.assertEqual("Menu " + name + " already exists",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_new_menu_incorrect_condition(self):
        name = "Menu_" + utils.generate_random_name()
        condition = "tryam"
        data = {"Name": name, "Value": "Item1", "ApplicationId": 1,
                "Conditions": condition}
        ans = self.call("NewMenu", data)
        self.assertEqual("unknown identifier " + condition,
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_menu(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        res = self.call("NewMenu", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = funcs.get_count(url, "menu", token)
        dataEdit = {"Id": count, "Value": "ItemEdited", "Conditions": "true"}
        res = self.call("EditMenu", dataEdit)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        content = {'tree': [{'tag': 'text', 'text': 'ItemEdited'}]}
        mContent = funcs.get_content(url, "menu", name, "", 1, token)
        self.assertEqual(mContent, content)

    def test_edit_incorrect_menu(self):
        id = "9999"
        dataEdit = {"Id": id, "Value": "ItemEdited", "Conditions": "true"}
        ans = self.call("EditMenu", dataEdit)
        msg = "Item " + id + " has not been found"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_edit_menu_incorrect_condition(self):
        name = "Menu_" + utils.generate_random_name()
        condition = "tryam"
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        res = self.call("NewMenu", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = funcs.get_count(url, "menu", token)
        dataEdit = {"Id": count, "Value": "ItemEdited", "Conditions": condition}
        ans = self.call("EditMenu", dataEdit)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_append_menu(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        res = self.call("NewMenu", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = funcs.get_count(url, "menu", token)
        dataEdit = {"Id": count, "Value": "AppendedItem", "Conditions": "true"}
        res = self.call("AppendMenu", dataEdit)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_append_incorrect_menu(self):
        id = "999"
        dataEdit = {"Id": id, "Value": "AppendedItem", "Conditions": "true"}
        ans = self.call("AppendMenu", dataEdit)
        msg = "Item " + id + " has not been found"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_page(self):
        name = "Page_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        content = [{'tag': 'text', 'text': 'Hello page!'}]
        cont = funcs.get_content(url, "page", name, "", 1, token)
        self.assertEqual(cont['tree'], content)

    def test_new_page_exist_name(self):
        name = "Page_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        ans = self.call("NewPage", data)
        msg = "Page " + name + " already exists"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_page_incorrect_condition(self):
        name = "Page_" + utils.generate_random_name()
        condition = "tryam"
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": condition, "Menu": "default_menu"}
        ans = self.call("NewPage", data)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_edit_page(self):
        name = "Page_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataEdit = {"Id": funcs.get_count(url, "pages", token),
                    "Value": "Good by page!", "Conditions": "true",
                    "Menu": "default_menu"}
        res = self.call("EditPage", dataEdit)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        content = [{'tag': 'text', 'text': 'Good by page!'}]
        pContent = funcs.get_content(url, "page", name, "", 1, token)
        self.assertEqual(pContent['tree'], content)

    def test_edit_page_with_validate_count(self):
        name = "Page_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "Conditions": "true",
                "ValidateCount": 6, "Menu": "default_menu",
                "ApplicationId": 1}
        res = self.call("NewPage", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataEdit = {"Id": funcs.get_count(url, "pages", token),
                    "Value": "Good by page!", "Conditions": "true",
                    "ValidateCount": 1, "Menu": "default_menu"}
        res = self.call("EditPage", dataEdit)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        content = [{'tag': 'text', 'text': 'Good by page!'}]
        pContent = funcs.get_content(url, "page", name, "", 1, token)
        self.assertEqual(pContent['tree'], content)

    def test_edit_incorrect_page(self):
        id = "9999"
        dataEdit = {"Id": id, "Value": "Good by page!",
                    "Conditions": "true", "Menu": "default_menu"} 
        ans = self.call("EditPage", dataEdit)
        self.assertEqual("Item " + id + " has not been found",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_page_incorrect_condition(self):
        name = "Page_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!",
                "Conditions": "true", "Menu": "default_menu",
                "ApplicationId": 1}
        res = self.call("NewPage", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        condition = "tryam"
        dataEdit = {"Id": funcs.get_count(url, "pages", token),
                    "Value": "Good by page!", "Conditions": condition,
                    "Menu": "default_menu"}
        ans = self.call("EditPage", dataEdit)
        self.assertEqual("unknown identifier " + condition,
                         ans["error"], "Incorrect message: " + str(ans))

    def test_append_page(self):
        name = "Page_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello!", "Conditions": "true",
                "Menu": "default_menu", "ApplicationId": 1}
        res = self.call("NewPage", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = funcs.get_count(url, "pages", token)
        dataEdit = {"Id": funcs.get_count(url, "pages", token),
                    "Value": "Good by!", "Conditions": "true",
                    "Menu": "default_menu"}
        res = self.call("AppendPage", dataEdit)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        content = [{'tag': 'text', 'text': 'Hello!\r\nGood by!'}]
        pContent = funcs.get_content(url, "page", name, "", 1, token)
        self.assertEqual(pContent['tree'], content)

    def test_append_page_incorrect_id(self):
        id = "9999"
        dataEdit = {"Id": id, "Value": "Good by!", "Conditions": "true",
                    "Menu": "default_menu"} 
        ans = self.call("AppendPage", dataEdit)
        msg = "Item " + id + " has not been found"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_block(self):
        name = "Block_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewBlock", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_block_exist_name(self):
        name = "Block_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewBlock", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        ans = self.call("NewBlock", data)
        self.assertEqual("Block " + name + " already exists",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_new_block_incorrect_condition(self):
        name = "Block_" + utils.generate_random_name()
        condition = "tryam"
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": condition}
        ans = self.call("NewBlock", data)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_edit_block_incorrect_id(self):
        id = "9999"
        dataEdit = {"Id": id, "Value": "Good by!", "Conditions": "true"}
        ans = self.call("EditBlock", dataEdit)
        msg = "Item " + id + " has not been found"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_edit_block(self):
        name = "Block_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello block!", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewBlock", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = funcs.get_count(url, "blocks", token)
        dataEdit = {"Id": count, "Value": "Good by!", "Conditions": "true"}
        res = self.call("EditBlock", dataEdit)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_edit_block_incorrect_condition(self):
        name = "Block_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello block!", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewBlock", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = funcs.get_count(url, "blocks", token)
        condition = "tryam"
        dataEdit = {"Id": count, "Value": "Good by!", "Conditions": condition}
        ans = self.call("EditBlock", dataEdit)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_table(self):
        column = """[{"name":"MyName","type":"varchar",
        "index": "1",  "conditions":"true"},{"name":"Myb","type":"json",
        "index": "0",  "conditions":"true"}, {"name":"MyD","type":"datetime",
        "index": "0",  "conditions":"true"}, {"name":"MyM","type":"money",
        "index": "0",  "conditions":"true"},{"name":"MyT","type":"text",
        "index": "0",  "conditions":"true"},{"name":"MyDouble","type":"double",
        "index": "0",  "conditions":"true"},{"name":"MyC","type":"character",
        "index": "0",  "conditions":"true"}]"""
        permission = """{"insert": "false",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "Tab_" + utils.generate_random_name(),
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        res = self.call("NewTable", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        
    def test_new_table_joint(self):
        columns = ["varchar", "Myb", "MyD", "MyM", "MyT", "MyDouble", "MyC"]
        types = ["varchar", "json", "datetime", "money", "text", "double", "character"]
        dicColumns = {"ColumnsArr[]": len(columns), "ColumnsArr[0]": columns[0],
                      "ColumnsArr[1]": columns[1], "ColumnsArr[2]": columns[2],
                      "ColumnsArr[3]": columns[3], "ColumnsArr[4]": columns[4],
                      "ColumnsArr[5]": columns[5], "ColumnsArr[6]": columns[6]}
        dicTypes = {"TypesArr[]": len(types), "TypesArr[0]": types[0],
                    "TypesArr[1]": types[1], "TypesArr[2]": types[2],
                    "TypesArr[3]": types[3], "TypesArr[4]": types[4],
                    "TypesArr[5]": types[5], "TypesArr[6]": types[6]}
        permission = """{"insert": "false",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "Tab_" + utils.generate_random_name(),
                "ApplicationId": 1, "TypesArr": dicTypes,
                "InsertPerm": "true", "UpdatePerm": "true",
                "NewColumnPerm": "true"}
        data.update(dicColumns)
        data.update(dicTypes)
        res = self.call("NewTableJoint", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_table_incorrect_column_name_digit(self):
        column = """[{"name":"123","type":"varchar",
        "index": "1",  "conditions":"true"}]"""
        permission = """{"insert": "false",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "Tab_" + utils.generate_random_name(),
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        ans = self.call("NewTable", data)
        msg = "Column name cannot begin with digit"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_table_incorrect_condition1(self):
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," +\
        "\"index\": \"1\",  \"conditions\":\"true\"}]"
        condition = "tryam"
        permissions = "{\"insert\": \"" + condition +\
        "\", \"\" : \"true\", \"new_column\": \"true\"}"
        data = {"Name": "Tab_" + utils.generate_random_name(),
                "Columns": columns, "Permissions": permissions,
                "ApplicationId": 1}
        ans = self.call("NewTable", data)
        self.assertEqual("unknown identifier " + condition,
                         ans["error"], "Incorrect message: " + str(ans))

    def test_new_table_incorrect_condition2(self):
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," +\
        "\"index\": \"1\",  \"conditions\":\"true\"}]"
        condition = "tryam"
        permissions = "{\"insert\": \"true\", \"update\" : \"" +\
        condition + "\", \"new_column\": \"true\"}"
        data = {"Name": "Tab_" + utils.generate_random_name(),
                "Columns": columns, "Permissions": permissions,
                "ApplicationId": 1}
        ans = self.call("NewTable", data)
        self.assertEqual("unknown identifier " + condition,
                         ans["error"], "Incorrect message: " + str(ans))

    def test_new_table_incorrect_condition3(self):
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," +\
        "\"index\": \"1\",  \"conditions\":\"true\"}]"
        condition = "tryam"
        permissions = "{\"insert\": \"true\", \"update\" : \"true\"," +\
        " \"new_column\": \"" + condition + "\"}"
        data = {"Name": "Tab_" + utils.generate_random_name(),
                "Columns": columns, "Permissions": permissions,
                "ApplicationId": 1}
        ans = self.call("NewTable", data)
        self.assertEqual("unknown identifier " + condition,
                         ans["error"], "Incorrect message: " + str(ans))

    def test_new_table_exist_name(self):
        name = "tab_" + utils.generate_random_name()
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," +\
        "\"index\": \"1\",  \"conditions\":\"true\"}]"
        permissions = "{\"insert\": \"false\", \"update\" : \"true\"," +\
        " \"new_column\": \"true\"}"
        data = {"Name": name, "Columns": columns,
                "Permissions": permissions, "ApplicationId": 1}
        res = self.call("NewTable", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        ans = self.call("NewTable", data)
        msg = "table " + name + " exists"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_table_identical_columns(self):
        name = "tab_" + utils.generate_random_name()
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," + \
        "\"index\": \"1\",  \"conditions\":\"true\"}," +\
        "{\"name\":\"MyName\",\"type\":\"varchar\"," +\
        "\"index\": \"1\",  \"conditions\":\"true\"}]"
        permissions = "{\"insert\": \"false\", \"update\": \"true\"," +\
        " \"new_column\": \"true\"}"
        data = {"Name": name, "Columns": columns,
                "Permissions": permissions, "ApplicationId": 1}
        ans = self.call("NewTable", data)
        self.assertEqual("There are the same columns", ans["error"],
                         "Incorrect message: " + str(ans))

    def test_edit_table(self):
        name = "Tab_" + utils.generate_random_name()
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," +\
        "\"index\": \"1\",  \"conditions\":\"true\"}]"
        permissions = "{\"insert\": \"false\", \"update\" : \"true\"," +\
        " \"new_column\": \"true\"}"
        data = {"Name": name, "Columns": columns,
                "Permissions": permissions, "ApplicationId": 1}
        res = self.call("NewTable", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataEdit = {"Name": name, "InsertPerm": "true",
                    "UpdatePerm": "true", "NewColumnPerm": "true"}
        res = self.call("EditTable", dataEdit)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_column(self):
        nameTab = "Tab_" + utils.generate_random_name()
        columns = """[{"name":"MyName","type":"varchar",
        "index": "1",  "conditions":"true"}]"""
        permissions = """{"insert": "false",
        "update" : "true","new_column": "true"}"""
        data = {"Name": nameTab, "Columns": columns,
                "Permissions": permissions, "ApplicationId": 1}
        res = self.call("NewTable", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataCol1 = {"TableName": nameTab, "Name": "var",
                   "Type": "varchar", "Index": "0", "Permissions": "true"}
        res1 = self.call("NewColumn", dataCol1)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataCol2 = {"TableName": nameTab, "Name": "json",
                   "Type": "json", "Index": "0", "Permissions": "true"}
        res2 = self.call("NewColumn", dataCol2)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataCol3 = {"TableName": nameTab, "Name": "num",
                   "Type": "number", "Index": "0", "Permissions": "true"}
        res3 = self.call("NewColumn", dataCol3)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataCol4 = {"TableName": nameTab, "Name": "date",
                   "Type": "datetime", "Index": "0", "Permissions": "true"}
        res4 = self.call("NewColumn", dataCol4)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataCol5 = {"TableName": nameTab, "Name": "sum",
                   "Type": "money", "Index": "0", "Permissions": "true"}
        res5 = self.call("NewColumn", dataCol5)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataCol6 = {"TableName": nameTab, "Name": "name",
                   "Type": "text", "Index": "0", "Permissions": "true"}
        res6 = self.call("NewColumn", dataCol6)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataCol7 = {"TableName": nameTab, "Name": "length",
                   "Type": "double", "Index": "0", "Permissions": "true"}
        res7 = self.call("NewColumn", dataCol7)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataCol8 = {"TableName": nameTab, "Name": "code",
                   "Type": "character", "Index": "0", "Permissions": "true"}
        res8 = self.call("NewColumn", dataCol8)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_edit_column(self):
        nameTab = "tab_" + utils.generate_random_name()
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," +\
        "\"index\": \"1\",  \"conditions\":\"true\"}]"
        permissions = "{\"insert\": \"false\", \"update\": \"true\"," +\
        " \"new_column\": \"true\"}"
        data = {"Name": nameTab, "Columns": columns,
                "Permissions": permissions, "ApplicationId": 1}
        res = self.call("NewTable", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        name = "Col_" + utils.generate_random_name()
        dataCol = {"TableName": nameTab, "Name": name, "Type": "number",
                   "Index": "0", "Permissions": "true"}
        res = self.call("NewColumn", dataCol)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataEdit = {"TableName": nameTab, "Name": name,
                    "Permissions": "false"}
        res = self.call("EditColumn", dataEdit)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_lang(self):
        data = {"AppID": "1", "Name": "Lang_" + utils.generate_random_name(),
                "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}",
                "ApplicationId": "1"}
        res = self.call("NewLang", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        
    def test_new_lang_joint(self):
        data = {"ApplicationId": 1,
                "Name": "Lang_" + utils.generate_random_name(),
                "ValueArr": ["en", "ru"], "LocaleArr": ["Hi", "Привет"]}
        res = self.call("NewLangJoint", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        
    def test_edit_lang_joint(self):
        data = {"ApplicationId": 1,
                "Name": "Lang_" + utils.generate_random_name(),
                "ValueArr": ["en", "ru"], "LocaleArr": ["Hi", "Привет"]}
        res = self.call("NewLangJoint", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = funcs.get_count(url, "languages", token)
        dataE = {"Id": count, "ValueArr": ["en", "de"],
                 "LocaleArr": ["Hi", "Hallo"]}
        res = self.call("EditLangJoint", dataE)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_edit_lang(self):
        name = "Lang_" + utils.generate_random_name()
        data = {"AppID": 1, "Name": name, "ApplicationId": 1,
                "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}"}
        res = self.call("NewLang", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = funcs.get_count(url, "languages", token)
        dataEdit = {"Id": count, "Name": name, "AppID": 1,
                    "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}"}
        res = self.call("EditLang", dataEdit)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_sign(self):
        name = "Sign_" + utils.generate_random_name()
        value = "{\"forsign\":\"" + name +\
        "\", \"field\": \"" + name + "\", \"title\": \"" + name +\
        "\", \"params\":[{\"name\": \"test\", \"text\": \"test\"}]}"
        data = {"Name": name, "Value": value, "Conditions": "true"}
        res = self.call("NewSign", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        
    def test_new_sign_joint(self):
        name = "Sign_" + utils.generate_random_name()
        params = [{"name": "test", "text": "test"},
                  {"name": "test2", "text": "test2"}]
        values = ["one", "two"]
        data = {"Name": name, "Title": name, "ParamArr": params,
                "ValueArr": values, "Conditions": "true"}
        res = self.call("NewSignJoint", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        
    def test_edit_sign_joint(self):
        name = "Sign_" + utils.generate_random_name()
        params = [{"name": "test", "text": "test"},
                  {"name": "test2", "text": "test2"}]
        values = ["one", "two"]
        data = {"Name": name, "Title": name, "ParamArr": params,
                "ValueArr": values, "Conditions": "true"}
        res = self.call("NewSignJoint", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = funcs.get_count(url, "signatures", token)
        dataE = {"Id": count, "Title": "NewTitle", "Parameter": str(params),
                 "Conditions": "true"}
        resE = self.call("EditSignJoint", dataE)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        
    def test_edit_sign(self):
        name = "Sign_" + utils.generate_random_name()
        value = "{\"forsign\":\"" + name +\
        "\", \"field\": \"" + name + "\", \"title\": \"" + name +\
        "\", \"params\":[{\"name\": \"test\", \"text\": \"test\"}]}"
        data = {"Name": name, "Value": value, "Conditions": "true"}
        res = self.call("NewSign", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = funcs.get_count(url, "signatures", token)
        valueE = "{\"forsign\": \"" + name + "\", \"field\": \"" +\
        name + "\", \"title\": \"" + name +\
        "\", \"params\":[{\"name\": \"test1\", \"text\": \"test2\"}]}"
        dataEdit = {"Id": count, "Value": valueE, "Conditions": "true"}
        res = self.call("EditSign", dataEdit)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_app_param(self):
        name = "param_"+utils.generate_random_name()
        data = {"ApplicationId": 1, "Name": name, "Value": "myParam", "Conditions": "true" }
        res = self.call("NewAppParam", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_edit_app_param(self):
        name = "param_"+utils.generate_random_name()
        data = {"ApplicationId": 1, "Name": name, "Value": "myParam", "Conditions": "true" }
        res = self.call("NewAppParam", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data2 = {"Id": 1, "Name": name, "Value": "myParamEdited", "Conditions": "true" }
        res = self.call("EditAppParam", data2)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_delayed_contracts(self):
        # add table for test
        column = """[{"name":"id_block","type":"number", "index": "1",  "conditions":"true"}]"""
        permission = """{"insert": "true", "update" : "true","new_column": "true"}"""
        table_name = "tab_delayed_" + utils.generate_random_name()
        data = {"Name": table_name, "Columns": column,
                "ApplicationId": 1, "Permissions": permission}
        res = self.call("NewTable", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # add contract which insert records in table in progress CallDelayedContract
        body = "{\n data{} \n conditions{} \n action { \n  DBInsert(\""+table_name+"\", \"id_block\", $block) \n } \n }"
        code, contract_name = utils.generate_name_and_code(body)
        data = {"Value": code, "ApplicationId": 1, "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # NewDelayedContract
        newLimit = 3
        data = {"Contract": contract_name, "EveryBlock": "1",
                "Conditions": "true", "Limit":newLimit}
        res = self.call("NewDelayedContract", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        old_block_id = int(res["blockid"])
        # get record id of 'delayed_contracts' table for run EditDelayedContract
        res = funcs.call_get_api(url + "/list/delayed_contracts", "", token)
        count = len(res["list"])
        id = res["list"][0]["id"]
        i = 1
        while i < count:
            if res["list"][i]["id"] > id:
                id = res["list"][i]["id"]
            i = i + 1
        # wait block_id until run CallDelayedContract
        self.waitBlockId(old_block_id, newLimit)
        # EditDelayedContract
        editLimit = 2
        data = {"Id":id, "Contract": contract_name, "EveryBlock": "1", "Conditions": "true", "Limit":editLimit}
        res = self.call("EditDelayedContract", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        old_block_id = res["blockid"]
        # wait block_id until run CallDelayedContract
        self.waitBlockId(old_block_id, editLimit)
        # verify records count in table
        count = funcs.get_count(url, table_name, token)
        self.assertEqual(int(count), newLimit+editLimit)

    def test_upload_binary(self):
        name = "image_"+utils.generate_random_name()
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        files = {'Data': file}
        data = [{"contract": "UploadBinary",
                 "params": {"File": 'Data', "Name": name, "ApplicationId": 1}}]
        resp = utils.call_multi_contract(url, prKey, data, token, files)
        res = self.assertTxInBlock(resp, token)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_update_system_parameters(self):
        data = {"Name": "max_block_user_tx", "Value" : "2"}
        res = self.call("UpdateSysParam", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_contract_recursive_call_by_name_action(self):
        contractName = "recur_" + utils.generate_random_name()
        body = """
        {
        data { }
        conditions { }
        action {
            Println("hello1")
            %s()
            }
        }
        """ % contractName
        code = utils.generate_code(contractName, body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        msg = "The contract can't call itself recursively"
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_contract_recursive_call_by_name_conditions(self):
        contractName = "recur_" + utils.generate_random_name()
        body = """
        {
        data { }
        conditions { 
            Println("hello1")
            %s()
            }
        action { }
        }
        """ % contractName
        code = utils.generate_code(contractName, body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        msg = "The contract can't call itself recursively"
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_contract_recursive_call_by_name_func_action(self):
        contractName = "recur_" + utils.generate_random_name()
        body = """
        {
        func runContract() int {
            %s()
            }
        data { }
        conditions { }
        action {
            runContract()
            }
        }
        """ % contractName
        code = utils.generate_code(contractName, body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        msg = "The contract can't call itself recursively"
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_contract_recursive_call_contract_action(self):
        contractName = "recur_" + utils.generate_random_name()
        body = """
        {
        data { }
        conditions { }
        action {
            Println("hello1")
            var par map
            CallContract("%s", par)
            }
        }
        """ % contractName
        code = utils.generate_code(contractName, body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        res = self.call(contractName, "")
        msg = "There is loop in @1" + contractName + " contract"
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_contract_recursive_call_contract_conditions(self):
        contractName = "recur_" + utils.generate_random_name()
        body = """
        {
        data { }
        conditions {
         Println("hello1")
            var par map
            CallContract("%s", par)
            }
        action { }
        }
        """ % contractName
        code = utils.generate_code(contractName, body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        res = self.call(contractName, "")
        msg = "There is loop in @1" + contractName + " contract"
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_contract_recursive_call_contract_func_conditions(self):
        contractName = "recur_" + utils.generate_random_name()
        body = """
        {
        func runContract() int {
            var par map
            CallContract("%s", par)
            }
        data { }
        conditions {
            runContract()
            }
        action { }
        }
        """ % contractName
        code = utils.generate_code(contractName, body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        res = self.call(contractName, "")
        msg = "There is loop in @1" + contractName + " contract"
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))
        
    def test_contract_memory_limit(self):
        # add contract with memory limit
        body = """
        {
        data {
            Count int "optional"
            }
        action {
            var a array
            while (true) {
                $Count = $Count + 1
                a[Len(a)] = JSONEncode(a)
                }
            }
        }
        """
        code, contract_name = utils.generate_name_and_code(body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # test
        data = ""
        msg = "Memory limit exceeded"
        res = self.call(contract_name, data)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_functions_recursive_limit(self):
        # add contract with recursive
        body = """
        {
        func myfunc(num int) int { 
            num = num + 1
            myfunc(num)
            }
        data{}
        conditions{}
        action {
            $a = 0
            myfunc($a)
            }
        }
        """
        code, contract_name = utils.generate_name_and_code(body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # test
        data = ""
        msg = "max call depth"
        res = self.call(contract_name, data)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_ei1_ExportNewApp(self):
        appID = 1
        data = {"ApplicationId": appID}
        res = self.call("ExportNewApp", data)
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_ei2_Export(self):
        appID = 1
        data = {}
        resExport = self.call("Export", data)
        founderID = utils.getFounderId(dbHost, dbName, login, pas)
        exportAppData = utils.getExportAppData(dbHost, dbName, login, pas, appID, founderID)
        jsonApp = str(exportAppData, encoding='utf-8')
        path = os.path.join(os.getcwd(), "fixtures", "exportApp1.json")
        with open(path, 'w', encoding='UTF-8') as f:
            data = f.write(jsonApp)
        if os.path.exists(path):
            fileExist = True
        else:
            fileExist = False
        mustBe = dict(resultExport=True,
                      resultFile=True)
        actual = dict(resultExport=int(resExport["blockid"])>0,
                      resultFile=fileExist)
        self.assertDictEqual(mustBe, actual, "test_Export is failed!")

    def test_ei3_ImportUpload(self):
        path = os.path.join(os.getcwd(), "fixtures", "exportApp1.json")
        with open(path, 'r') as f:
            file = f.read()
        files = {'input_file': file}
        data = [{"contract": "ImportUpload",
                 "params": {"File": 'input_file'}}]
        resp = utils.call_multi_contract(url, prKey, data,
                                         token, files)
        resImportUpload = self.assertTxInBlock(resp, token)
        self.assertGreater(resImportUpload["blockid"], 0,
                           "BlockId is not generated: " + str(resImportUpload))

    def test_ei4_Import(self):
        founderID = utils.getFounderId(dbHost, dbName, login, pas)
        importAppData = utils.getImportAppData(dbHost, dbName, login, pas, founderID)
        importAppData = importAppData['data']
        contractName = "Import"
        data = [{"contract": contractName,
                 "params": importAppData[i]} for i in range(len(importAppData))]
        self.call(contractName, data)


if __name__ == '__main__':
    unittest.main()
