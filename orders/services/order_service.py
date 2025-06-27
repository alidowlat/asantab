class OrderCalculator:
    """" using encapsulation """

    def __init__(self, order):
        self.order = order

    def total_price(self):
        return sum(item.final_price for item in self.order.items.all())

    def total_discount(self):
        return sum(item.discount_amount or 0 for item in self.order.items.all())

    def discounted_price(self):
        return self.total_price() - self.total_discount()
