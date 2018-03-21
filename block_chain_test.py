import unittest
import utils
import config
import requests
import time
import funcs
from builtins import sum

class BlockChainTestCase(unittest.TestCase):

    def create_contract(self, url, prKey):
        code,name = utils.generate_name_and_code("")
        data = {'Wallet': '', 'Value': code, 'Conditions': "ContractConditions(`MainCondition`)"}
        resp = utils.call_contract(url, prKey, "NewContract", data, self.data1["jwtToken"])
        return name
    
    def test_block_chain(self):
        fullConfig = config.getNodeConfig()
        config1 = fullConfig["1"]
        config2 = fullConfig["2"]
        db1 = config1["dbName"]
        db2 = config2["dbName"]
        login1 = config1["login"]
        login2 = config2["login"]
        pas1 = config1["pass"]
        pas2 = config2["pass"]
        host1 = config1["dbHost"]
        host2 = config2["dbHost"]
        ts_count = 30
        self.data1 = utils.login(config1["url"], config1['private_key'])
        i = 1
        while i < ts_count:
            contName = self.create_contract(config1["url"], config1['private_key'])
            i = i + 1
            time.sleep(1)
        time.sleep(120)
        count_contracts1 = utils.getCountDBObjects(host1, db1, login1, pas1)["contracts"]
        count_contracts2 = utils.getCountDBObjects(host2, db2, login2, pas2)["contracts"]
        amounts1 = utils.getUserTokenAmounts(host1, db1, login1, pas1)
        amounts2 = utils.getUserTokenAmounts(host2, db2, login2, pas2)
        sumAmounts = sum(amount[0] for amount in amounts1)
        maxBlockId1 = funcs.get_max_block_id(config1["url"],self.data1["jwtToken"])
        self.data2 = utils.login(config2["url"], config1['private_key'])
        maxBlockId2 = funcs.get_max_block_id(config2["url"],self.data2["jwtToken"])
        maxBlock = max(maxBlockId2, maxBlockId1)
        hash1 = utils.get_blockchain_hash(host1, db1, login1, pas1, maxBlock)
        hash2 = utils.get_blockchain_hash(host2, db2, login2, pas2, maxBlock)
        node_position = utils.compare_node_positions(host1, db1, login1, pas1, maxBlock)
        dict1 = dict(count_contract = str(count_contracts1),
                     amounts = str(amounts1), summ = str(sumAmounts),
                     hash = str(hash1),
                     node_pos = str(node_position))
        dict2 = dict(count_contract = str(count_contracts2),
                     amounts = str(amounts2),
                     summ = 100000000000000000100000000,
                     hash = str(hash2),
                     node_pos = "True")
        msg = "Test two_nodes is faild. contracts: \n"
        msg += str(count_contracts1) + str(amounts1) + str(hash1) + str(node_position) + "\n"
        msg += str(count_contracts2) + str(amounts1) + str(hash1) + str(node_position) + "\n"
        msg += "Amounts summ: " + str(sumAmounts)
        self.assertDictEqual(dict1, dict2, msg)

        
if __name__ == "__main__":
    unittest.main()
    
