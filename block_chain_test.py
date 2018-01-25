import unittest
import utils
import config
import requests
import time
import argparse
import sys

class BlockChainTestCase(unittest.TestCase):

    def get_name_and_code(self):
        name = utils.generate_random_name()
        code = """contract %s {
                       conditions {}
                       action {}
                    }""" % (name,)
        return code,name
    
    def generate_code(self, name):
        code = """contract %s {
                       conditions {}
                       action {
                       var test string}
                    }""" % (name,)
        return code

    def create_contract(self):
        code,name = self.get_name_and_code()
        data = {'Wallet': '', 'Value': code, 'Conditions': """ContractConditions(`MainCondition`)"""}
        resp = utils.call_contract("NewContract", data, self.data["jvtToken"])
        return name
    
    def test_block_chain(self):
        db1 = args.dbName1
        db2 = args.dbName2
        login = args.dbUser
        pas = args.dbPassword
        host = args.dbHost

        ts_count = 30
        config.readMainConfig()
        self.data = utils.login()
        i = 1
        while i < ts_count:
            start = time.time()
            contName = self.create_contract()
            i = i + 1
            sleep = int(args.sleep) - (time.time() - start)
            if sleep < 0:
                print("Request is too long")
                exit(1)
            time.sleep(sleep)
        time.sleep(15)
        self.assertTrue(utils.get_count_records_block_chain(host, db1, login, pas), "There isn't 30 records in block_chain1")
        self.assertTrue(utils.get_count_records_block_chain(host, db2, login, pas), "There isn't 30 records in block_chain2")
        count_contracts1 = utils.getCountDBObjects(host, db1, login, pas)["contracts"]
        count_contracts2 = utils.getCountDBObjects(host, db2, login, pas)["contracts"]
        self.assertTrue(utils.compare_keys_cout(host, db2, login, pas), "There are different count of keys in block_chain")
        self.assertTrue(utils.compare_node_positions(host, db1, login, pas), "Incorrect order of nodes in block_chain")
        self.assertEqual(count_contracts1, count_contracts2,"Different count")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-dbHost', default='localhost')
    parser.add_argument('-dbPort', default='5432')
    parser.add_argument('-dbUser', default='postgres')
    parser.add_argument('-dbPassword', default='postgres')
    parser.add_argument('-dbName1', default='apla')
    parser.add_argument('-dbName2', default='apla2')
    parser.add_argument('-sleep', default='1')

    args = parser.parse_args()
    del(sys.argv[1:])

    unittest.main()
    
