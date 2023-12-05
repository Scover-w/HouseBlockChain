from typing import List
import uuid
import datetime







class Investor:

    def __init__(self):
        self.UUID = uuid.uuid5()
        self.bankAccount = 0
        self.tokenOwns = []
        self.buildings = []

    def addBuilding(self, amount, nbToken, nameBuilding):
        new_building = Building(nameBuilding, self, nbToken, amount)
        self.buildings.append(new_building)
        tokens_building = new_building.tokens
        for token_building in tokens_building:
            self.tokenOwns.append(token_building)

    def receiveRent(self, amount, building):
        building.receiveRent(amount)

    def receiveMoney(self, amount):
        self.bankAccount += amount
    
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
        self.UUID = uuid.uuid5()
        self.name = name
        self.proprietary = proprietary
        self.tokens:List[Token]= []
        self.token_price = building_price/nbToken
        for i in range(nbToken):
            self.tokens.append(Token(self, proprietary))

    def receiveRent(self, amount_rent):
        amount_per_token = amount_rent/len(self.tokens)
        for token in self.tokens:
            token.payInvestor(amount_per_token)

class Token:

    def __init__(self, building : Building, investor : Investor):
        self.UUID = uuid.uuid5()
        self.building = building
        self.investor = investor

    def payInvestor(self, amount):
        self.investor.receiveMoney(amount)

    def replaceInvestor(self, new_investor):
        previous_investor = self.investor
        self.investor = new_investor
        previous_investor.tokenOwns.remove(self)



def main():
    i = 5

if __name__ == "__main__":
    main()