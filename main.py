from typing import List
import uuid
import datetime
import hashlib
import json
import os

'''
    Investor Creation
    Receive Money Investor
    House creation
        Tokens creation
    Transaction Tokens
        Switch Investor
        Receive Money
        Send Money
    Receive Rent
        Receive Money
'''


class Blockchain:

    instance = None

    def __init__(self, db_path):
        
        if Blockchain.instance != None:
            raise ValueError("A blockchain has already been created")
        
        # Currently remove the db because the reading feature isn't implemented yet 
        os.remove(db_path)
        does_db_exist = os.path.exists(db_path)

        Blockchain.instance = self
        self.investors = []
        self.blocks = []
        self.db_path = db_path

        if not does_db_exist:
            self.currentBlock = Block("00000000-0000-0000-0000-000000000000")
            open(db_path, 'w')
            return
    

    def createInvestor(self, name):
        investor = Investor(name)
        self.investors.append(investor)

        transactionBatch = { "transaction_key" : "INVESTOR_CREATION",
                             "transaction_body" : {"UUID" : str(investor.UUID),
                                                   "Name" : investor.name,
                                                    "TransactionDate" : dateToString(datetime.datetime.now())}}

        self.addTransactionBatch(transactionBatch)
    
    def addTransactionBatch(self, transaction_batch):
        
        self.currentBlock.addTransactionBatch(transaction_batch)

        if not self.currentBlock.isFull():
            return
        
        blockTxt = self.currentBlock.toTxt()

        with open(self.db_path, 'a') as db_file:
            db_file.write(blockTxt)

        previous_hash = self.currentBlock.hash
        self.currentBlock = Block(previous_hash)

           


    

class Block:


    def __init__(self, previousHash, blockTxt = None):

        if blockTxt == None:
            self.previousHash = previousHash
            self.hash = None
            self.creationDate = datetime.datetime.now()
            self.endDate = None
            self.transaction_batchs = []
            return
        

    def addTransactionBatch(self, transaction_batch):
        self.transaction_batchs.append(transaction_batch)

    def isFull(self):
        return len(self.transaction_batchs) >= 2        
    
    def getHash(self):
        blockTxt = ""
        blockTxt += self.previousHash + dateToString(self.creationDate) + dateToString(self.endDate)

        blockTxt += json.dumps(self.transaction_batchs)

        return hashlib.sha256(blockTxt.encode()).hexdigest()


    def toTxt(self):

        self.endDate = datetime.datetime.now()
        self.hash = self.getHash()

        blockTxt = "/NEXT_BLOCK/\n"

        block = { 
                    "previousHash" : self.previousHash,
                    "hash" : self.hash,
                    "creationDate" : dateToString(self.creationDate),
                    "endDate" : dateToString(self.endDate),
                    "transactions" : json.dumps(self.transaction_batchs)
                }
        
        blockTxt += json.dumps(block) + "\n"
        return blockTxt




class Investor:

    def __init__(self, name):
        self.UUID = uuid.uuid4()
        self.name = name
        self.bankAccount = 0
        self.tokenOwns = []
        self.buildings = []

    def addBuilding(self, building_price, nbToken, nameBuilding):
        new_building = Building(nameBuilding, self, nbToken, building_price)
        self.buildings.append(new_building)
        tokens_building = new_building.tokens

        tokens = []

        for token_building in tokens_building:
            self.tokenOwns.append(token_building)
            tokens.append({ "TokenUUID" : str(token_building.UUID)})


        transactionBatch = { "transaction_key" : "TOKENIZE_BUILDING",
                             "transaction_body" : {"InvestorUUID" : str(self.UUID),
                                                   "BuildingUUID" : str(new_building.UUID),
                                                   "BuildingName" : nameBuilding,
                                                   "BuildingPrice" : str(building_price),
                                                   "Tokens" : json.dumps(tokens),
                                                    "TransactionDate" : dateToString(datetime.datetime.now())}}
        
        Blockchain.instance.addTransactionBatch(transactionBatch)

    def receiveRent(self, amount, building):
        building.receiveRent(amount)


    def receiveRentToken(self, amount, token):
        self.bankAccount += amount

        transactionMiniBatch = { "TokenUUID" : str(token.UUID), "InvestorUUID" : str(self.UUID), "Amount" : str(amount) }
        return transactionMiniBatch


    def receiveMoney(self, amount):
        self.bankAccount += amount

        transactionBatch = { "transaction_key" : "INVESTOR_RECEIVE_MONEY",
                             "transaction_body" : {"UUID" : str(self.UUID),
                                                   "Name" : self.name,
                                                   "Amount" : str(amount),
                                                    "TransactionDate" : dateToString(datetime.datetime.now())}}

        Blockchain.instance.addTransactionBatch(transactionBatch)
    
    def tryBuyToken(self, token):
        priceToken = token.building.token_price
        if self.bankAccount < priceToken:
            return False
        self.bankAccount-=priceToken    
        self.tokenOwns.append(token)  
        token.replaceInvestor(self)

        return True

class Building:

    def __init__(self, name, proprietary, nbToken, building_price):
        self.UUID = uuid.uuid4()
        self.name = name
        self.proprietary = proprietary
        self.tokens:List[Token]= []
        self.token_price = building_price/nbToken
        for i in range(nbToken):
            self.tokens.append(Token(self, proprietary))

    def receiveRent(self, amount_rent):
        amount_per_token = amount_rent/len(self.tokens)

        transactions_mini_batchs = []

        for token in self.tokens:
            transactions_mini_batchs.append(token.payInvestor(amount_per_token))


        transactionBatch = { "transaction_key" : "RECEIVE_RENT",
                             "transaction_body" : {"BuildingUUID" : str(self.UUID),
                                                    "RentUUID" : str(uuid.uuid4()),
                                                    "TransactionDate" : dateToString(datetime.datetime.now()),
                                                    "Tokens" : json.dumps(transactions_mini_batchs)
                                                    }}

        Blockchain.instance.addTransactionBatch(transactionBatch)

class Token:

    def __init__(self, building : Building, investor : Investor):
        self.UUID = uuid.uuid4()
        self.building = building
        self.investor = investor

    def payInvestor(self, amount):
        return self.investor.receiveRentToken(amount, self)

    def replaceInvestor(self, new_investor):
        previous_investor = self.investor
        self.investor = new_investor
        previous_investor.tokenOwns.remove(self)





def displayInvestors(blockchain:Blockchain):
    i = 0
    for investor in blockchain.investors:
        print(i, ". ", investor.name)
        i += 1



def createInvestor():
    name_investor = input("Name of the investor :\n> ")
    Blockchain.instance.createInvestor(name_investor)

def selectInvestor():
    displayInvestors(Blockchain.instance)
    id_investor = input("Id Investor to select : \n> ")
    return Blockchain.instance.investors[int(id_investor)]

def tranferMoney(selected_investor):

    if selected_investor == None:
        print("No investor selected !")
        return
    
    amount = input("Write amount :\n> ")
    print(selected_investor.bankAccount)
    selected_investor.receiveMoney(int(amount))
    print(selected_investor.bankAccount)

def tokenizeBuilding(selected_investor : Investor):

    if selected_investor == None:
        print("No investor selected !")
        return

    name = input("Building name :\n> ")
    building_price = int(input("Building price :\n> "))
    nbToken = int(input("Token number to split :\n> "))

    selected_investor.addBuilding(building_price, nbToken, name)

def selectBuilding(selected_investor : Investor):

    if selected_investor == None:
        print("No investor selected !")
        return None

    i = 0
    for building in selected_investor.buildings:
        print(i, ". ", building.name)
        i += 1

    building_id = input("Select building id :\n> ")
    return selected_investor.buildings[int(building_id)]

def retrieveRent(selected_investor : Investor, selected_building: Building):
    amount = int(input("Amount of the rent :\n> "))
    selected_investor.receiveRent(amount, selected_building)



def main():
    
    file_name = "blockchainDb.txt"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, file_name)

    blockchain = Blockchain(file_path)
    os.system('cls')


    selected_investor = None
    selected_building = None

    while(True):
        print("Data :  -----------------------")
        if selected_investor != None:
            print("Selected investor : ", selected_investor.name)

        if selected_building != None:
            print("Selected building : ", selected_building.name)

        print("------------------------------\n\n")

        print("Quelle action souhaitez vous effectuer ?")
        print("1. Add investor")
        print("2. Select investor")

        if(selected_investor != None):
            print("3. Transfer money to investor")
            print("4. Tokenize new building")
            print("5. Select building")

            if(selected_building != None):
                print("6. Retrieve rent")

        print("\nQ. Leave\n\n")
        action = input("> ")
        os.system('cls')


        if action == "1":
            createInvestor()
            
        elif action == "2":
            selected_investor = selectInvestor()

        elif action == "3":
            tranferMoney(selected_investor)

        elif action == "4":
            tokenizeBuilding(selected_investor)

        elif action == "5":
            selected_building = selectBuilding(selected_investor)

        elif action == "6":
            selected_building = retrieveRent(selected_investor, selected_building)

        elif action == "q":
            return

        

def dateToString(date: datetime):
    return date.strftime("%Y-%m-%d %H:%M:%S")

    

if __name__ == "__main__":
    main()