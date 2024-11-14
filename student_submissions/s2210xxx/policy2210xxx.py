from policy import Policy


def Policy2210xxx(Policy):
    def __init__(self):
        # Student code here
        pass

    def get_action(self, observation, info):
        # Student code here
        pass

    # Student code here
    # You can add more functions if needed


class Policy2211960(Policy):
    def __init__(self):
        self.sWidth = None
        self.sHeight = None

    def getStockSize(self):
        
        return self.sWidth * self.sHeight
    
    def get_action(self, observation, info):

        # Sort products by their areas in descending order
        proSortedList = sorted(
            observation["products"], # List of products' information
            key=lambda prod: prod["size"][0] * prod["size"][1], # Products' area
            reverse=True # Set descending order
        )

        productSize = [0, 0]
        stockID = -1
        pos_x, pos_y = 0, 0

        # Iterate over sorted products list
        for prod in proSortedList:
            if prod["quantity"] > 0:
                productSize = prod["size"]
                productW, productH = productSize

                # Find suitable stock for valid position to place product
                for i, stock in enumerate(observation["stocks"]):
                    stockW, stockH = self._get_stock_size_(stock)
                    self.sWidth = stockW
                    self.sHeight = stockH

                    # If stock's size is smaller than product's, pass it
                    if stockW < productW or stockH < productH:
                        continue

                    # Check all possible position in stock if it's fit to cut product 
                    pos_x, pos_y = None, None
                    for x in range(stockW - productW + 1):
                        for y in range(stockH - productH + 1):
                            if self._can_place_(stock, (x, y), productSize):
                                # If this position is adapted, save it and stop checking other position in height
                                pos_x, pos_y = x, y 
                                break
                        # If position is found, stop checking other position in width
                        if pos_x is not None and pos_y is not None:
                            break
                    # If position is found, store the index of stock
                    if pos_x is not None and pos_y is not None:
                        stockID = i
                        break
                # If position is found, break and return information of action
                if pos_x is not None and pos_y is not None:
                    break

        return {"stock_idx": stockID, "size": productSize, "position": (pos_x, pos_y)}
