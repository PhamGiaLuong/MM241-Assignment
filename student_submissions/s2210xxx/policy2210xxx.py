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

# Dynamic Programming
## Tìm vị trí tốt nhất để đặt product hiện tại
## Hao phí được tính theo số lượng ô trống (lãng phí) xung quanh product
## Cache vị trí tốt nhất để đặt prod_size vào trạng thái 1 stock (tính theo quick waste)
class Policy2313109(Policy):
    def __init__(self):
        # Cache best_pos_in_stock thay vì waste vì quy mô lớn hơn
        # Một giá trị cache có hiệu lực cho đến khi trạng thái stock đó thay đổi
        self.best_pos_in_stock_cache = {}
        
    def get_action(self, observation, info):
        # Sort products theo diện tích giảm dần
        products = sorted(observation["products"], 
                        key=lambda x: x["size"][0] * x["size"][1],
                        reverse=True)
        stocks = observation["stocks"]
        
        # Lấy product để đặt
        for prod in products:
            if prod["quantity"] > 0:
                # Tìm vị trí tốt nhất để đặt product
                best_pos = None
                best_pos = self.get_best_pos(stocks, prod)
                # Trả best pos
                if best_pos:
                    stock_idx, (pos_x, pos_y) = best_pos
                    return {
                        "stock_idx": stock_idx,
                        "size": prod["size"],
                        "position": (pos_x, pos_y)
                    }
        
        # Trả action mặc định nếu không tìm được vị trí đặt
        return {"stock_idx": -1, "size": [0, 0], "position": (0, 0)}
    
    def get_best_pos(self, stocks, product):
        # Tìm vị trí tốt nhất để đặt product trong tất cả các stock
        # Phạm vi duyệt từng stock
        # Lấy best_in_stock của từng stock, tính true waste để lấy best_in_stock tốt nhất
        prod_w, prod_h = product["size"]
        
        best_pos = None
        min_waste = float('inf')
        
        # Duyệt qua các stock
        for stock_idx, stock in enumerate(stocks):
            stock_w, stock_h = self._get_stock_size_(stock)
            # Bỏ qua stock quá nhỏ
            if stock_w < prod_w or stock_h < prod_h:
                continue
            
            # Lấy best_in_stock = vị trí tốt nhất cho stock hiện tại theo quick waste
            # Lấy từ cache nếu có, tính toán nếu không
            cache_key = (stock.tobytes(), prod_w, prod_h)
            if cache_key in self.best_pos_in_stock_cache:
                best_in_stock = self.best_pos_in_stock_cache[cache_key]
            else:
                best_in_stock = self.best_pos_in_stock(stock, product["size"])
                self.best_pos_in_stock_cache[cache_key] = best_in_stock
            
            # True waste chỉ tính cho best_in_stock để đảm bảo hiệu năng
            if best_in_stock:
                waste = self.true_waste(stock, best_in_stock, product["size"])
                if waste < min_waste:
                    min_waste = waste
                    best_pos = (stock_idx, best_in_stock)
        
        # best_pos = (stock_idx, (x, y))
        return best_pos

    def best_pos_in_stock(self, stock, prod_size):
        # Tìm vị trí tốt nhất để đặt product trong MỘT stock theo quick waste
        # Phạm vi duyệt từng vị trí trong stock
        # Sử dụng quick waste để đảm bảo đặt sát các góc
        stock_w, stock_h = self._get_stock_size_(stock)
        prod_w, prod_h = prod_size
        
        # Init best_pos_in_stock & min_waste
        best_pos_in_stock = None
        min_waste = float('inf')
        
        # Các vị trí khả thi
        for x in range(stock_w - prod_w + 1):
            for y in range(stock_h - prod_h + 1):
                if self._can_place_(stock, (x, y), prod_size):
                    # Tính waste (hao phí) của vị trí
                    waste = self.quick_waste(stock, (x, y), prod_size)
                    # Cập nhật best_pos_in_stock nếu min waste
                    if waste < min_waste:
                        min_waste = waste
                        best_pos_in_stock = (x, y)

        # best_pos_in_stock = (x, y)
        return best_pos_in_stock
    
    def quick_waste(self, stock, position, prod_size):
        # Tính hao phí của vị trí đặt product
        # Hao phí được tính theo số lượng ô trống xung quanh product
        # Xét phạm vi 1 ô xung quanh product
        pos_x, pos_y = position
        prod_w, prod_h = prod_size
        waste = 0
        
        # Quét cạnh dưới +1 (block kích thước prod_w x 1)
        y = pos_y + prod_h  # cạnh dưới
        for x in range(pos_x, pos_x + prod_w):
            if (0 <= x < stock.shape[0] and 
                0 <= y < stock.shape[1] and 
                stock[x, y] == -1):
                waste += 1
                
        # Quét cạnh trên +1 (block kích thước prod_w x 1)
        y = pos_y - 1  # cạnh trên
        for x in range(pos_x, pos_x + prod_w):
            if (0 <= x < stock.shape[0] and 
                0 <= y < stock.shape[1] and 
                stock[x, y] == -1):
                waste += 1
                
        # Quét cạnh phải +1 (block kích thước 1 x prod_h)
        x = pos_x + prod_w  # cạnh phải
        for y in range(pos_y, pos_y + prod_h):
            if (0 <= x < stock.shape[0] and 
                0 <= y < stock.shape[1] and 
                stock[x, y] == -1):
                waste += 1
                
        # Quét cạnh trái +1 (block kích thước 1 x prod_h)
        x = pos_x - 1  # cạnh trái
        for y in range(pos_y, pos_y + prod_h):
            if (0 <= x < stock.shape[0] and 
                0 <= y < stock.shape[1] and 
                stock[x, y] == -1):
                waste += 1
                
        return waste
    
    def true_waste(self, stock, position, prod_size):
        # True waste
        # Tương tự quick waste nhưng quét các hướng cho đến hết biên stock
        pos_x, pos_y = position
        prod_w, prod_h = prod_size
        waste = 0
        
        # Quét từ cạnh dưới ra (block kích thước prod_w x ?)
        for x in range(pos_x, pos_x + prod_w):
            y = pos_y + prod_h  # bắt đầu từ cạnh dưới
            while (0 <= x < stock.shape[0] and 
                0 <= y < stock.shape[1] and 
                stock[x, y] == -1):
                waste += 1
                y += 1  # bước xuống dưới
                    
        # Quét từ cạnh trên ra (block kích thước prod_w x ?)
        for x in range(pos_x, pos_x + prod_w):
            y = pos_y - 1  # bắt đầu từ cạnh trên
            while (0 <= x < stock.shape[0] and 
                0 <= y < stock.shape[1] and 
                stock[x, y] == -1):
                waste += 1
                y -= 1  # bước lên trên
                    
        # Quét từ cạnh phải ra (block kích thước ? x prod_h)
        for y in range(pos_y, pos_y + prod_h):
            x = pos_x + prod_w  # bắt đầu từ cạnh phải
            while (0 <= x < stock.shape[0] and 
                0 <= y < stock.shape[1] and 
                stock[x, y] == -1):
                waste += 1
                x += 1  # bước sang phải
                    
        # Quét từ cạnh trái ra (block kích thước ? x prod_h)
        for y in range(pos_y, pos_y + prod_h):
            x = pos_x - 1  # bắt đầu từ cạnh trái
            while (0 <= x < stock.shape[0] and 
                0 <= y < stock.shape[1] and 
                stock[x, y] == -1):
                waste += 1
                x -= 1  # bước sang trái
                    
        return waste