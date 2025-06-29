class OrderCalculator:
    def __init__(self, order):
        self.order = order

    def total_price(self):
        return sum(item.final_price for item in self.order.items.all())

    def discount_amount(self):
        if self.order.discount_code:
            if self.order.discount_code.amount:
                return self.order.discount_code.amount
            if self.order.discount_code.percent:
                return (self.total_price() * self.order.discount_code.percent) / 100
        return 0

    def final_price(self):
        return self.total_price() - self.discount_amount()