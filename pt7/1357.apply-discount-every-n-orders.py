#
# @lc app=leetcode id=1357 lang=python3
#
# [1357] Apply Discount Every n Orders
#
# https://leetcode.com/problems/apply-discount-every-n-orders/description/
#
# algorithms
# Medium (65.55%)
# Likes:    216
# Dislikes: 234
# Total Accepted:    29.9K
# Total Submissions: 45.7K
# Testcase Example:  '["Cashier","getBill","getBill","getBill","getBill","getBill","getBill","getBill"]\n' +
# '[[3,50,[1,2,3,4,5,6,7],[100,200,300,400,300,200,100]],[[1,2],[1,2]],[[3,7],[10,10]],[[1,2,3,4,5,6,7],[1,1,1,1,1,1,1]],[[4],[10]],[[7,3],[10,10]],[[7,5,3,1,6,4,2],[10,10,10,9,9,9,7]],[[2,3,5],[5,3,2]]]'
#
# There is a supermarket that is frequented by many customers. The products
# sold at the supermarket are represented as two parallel integer arrays
# products and prices, where the i^th product has an ID of products[i] and a
# price of prices[i].
# 
# When a customer is paying, their bill is represented as two parallel integer
# arrays product and amount, where the j^th product they purchased has an ID of
# product[j], and amount[j] is how much of the product they bought. Their
# subtotal is calculated as the sum of each amount[j] * (price of the j^th
# product).
# 
# The supermarket decided to have a sale. Every n^th customer paying for their
# groceries will be given a percentage discount. The discount amount is given
# by discount, where they will be given discount percent off their subtotal.
# More formally, if their subtotal is bill, then they would actually pay bill *
# ((100 - discount) / 100).
# 
# Implement the Cashier class:
# 
# 
# Cashier(int n, int discount, int[] products, int[] prices) Initializes the
# object with n, the discount, and the products and their prices.
# double getBill(int[] product, int[] amount) Returns the final total of the
# bill with the discount applied (if any). Answers within 10^-5 of the actual
# value will be accepted.
# 
# 
# 
# Example 1:
# 
# 
# Input
# 
# ["Cashier","getBill","getBill","getBill","getBill","getBill","getBill","getBill"]
# 
# [[3,50,[1,2,3,4,5,6,7],[100,200,300,400,300,200,100]],[[1,2],[1,2]],[[3,7],[10,10]],[[1,2,3,4,5,6,7],[1,1,1,1,1,1,1]],[[4],[10]],[[7,3],[10,10]],[[7,5,3,1,6,4,2],[10,10,10,9,9,9,7]],[[2,3,5],[5,3,2]]]
# Output
# [null,500.0,4000.0,800.0,4000.0,4000.0,7350.0,2500.0]
# Explanation
# Cashier cashier = new
# Cashier(3,50,[1,2,3,4,5,6,7],[100,200,300,400,300,200,100]);
# cashier.getBill([1,2],[1,2]);                        // return 500.0. 1^st
# customer, no discount.
# ⁠                                                    // bill = 1 * 100 + 2 *
# 200 = 500.
# cashier.getBill([3,7],[10,10]);                      // return 4000.0. 2^nd
# customer, no discount.
# ⁠                                                    // bill = 10 * 300 + 10
# * 100 = 4000.
# cashier.getBill([1,2,3,4,5,6,7],[1,1,1,1,1,1,1]);    // return 800.0. 3^rd
# customer, 50% discount.
# ⁠                                                    // Original bill = 1600
# ⁠                                                    // Actual bill = 1600 *
# ((100 - 50) / 100) = 800.
# cashier.getBill([4],[10]);                           // return 4000.0. 4^th
# customer, no discount.
# cashier.getBill([7,3],[10,10]);                      // return 4000.0. 5^th
# customer, no discount.
# cashier.getBill([7,5,3,1,6,4,2],[10,10,10,9,9,9,7]); // return 7350.0. 6^th
# customer, 50% discount.
# ⁠                                                    // Original bill =
# 14700, but with
# ⁠                                                    // Actual bill = 14700 *
# ((100 - 50) / 100) = 7350.
# cashier.getBill([2,3,5],[5,3,2]);                    // return 2500.0.  7^th
# customer, no discount.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 10^4
# 0 <= discount <= 100
# 1 <= products.length <= 200
# prices.length == products.length
# 1 <= products[i] <= 200
# 1 <= prices[i] <= 1000
# The elements in products are unique.
# 1 <= product.length <= products.length
# amount.length == product.length
# product[j] exists in products.
# 1 <= amount[j] <= 1000
# The elements of product are unique.
# At most 1000 calls will be made to getBill.
# Answers within 10^-5 of the actual value will be accepted.
# 
# 
#

# @lc code=start
from __future__ import annotations

from typing import List


class Cashier:

    def __init__(self, n: int, discount: int, products: List[int], prices: List[int]):
        self.n = n
        self.discount = discount
        self.customer_count = 0
        self.price_by_product = dict(zip(products, prices))

    def getBill(self, product: List[int], amount: List[int]) -> float:
        self.customer_count += 1
        total = 0

        for product_id, quantity in zip(product, amount):
            total += self.price_by_product[product_id] * quantity

        if self.customer_count % self.n == 0:
            total *= (100 - self.discount) / 100

        return total


# Your Cashier object will be instantiated and called as such:
# obj = Cashier(n, discount, products, prices)
# param_1 = obj.getBill(product,amount)
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# Store product prices for O(1) lookup and keep a running customer count. Every
# nth customer receives the discount.
#
# Data structure:
# A dictionary maps product id to price. Integers track the discount rule and
# how many bills have been processed.
#
# Walkthrough:
# 1. Constructor zips `products` and `prices` into a lookup table.
# 2. `getBill` increments the customer count.
# 3. Sum `price * amount` for each item in the order.
# 4. If this is the nth, 2nth, 3nth, ... customer, apply the percentage
#    discount.
#
# Edge cases:
# - Order with multiple products: zip pairs each product with its quantity.
# - Discount customer: multiplication by `(100 - discount) / 100` gives the
#   final bill.
# - Non-discount customer: total is returned unchanged.
#
# Complexity:
# - Constructor: O(p), where p is number of products.
# - `getBill`: O(k), where k is number of product ids in the current order.
# - Space: O(p).
