#
# @lc app=leetcode id=1352 lang=python3
#
# [1352] Product of the Last K Numbers
#
# https://leetcode.com/problems/product-of-the-last-k-numbers/description/
#
# algorithms
# Medium (63.02%)
# Likes:    2179
# Dislikes: 110
# Total Accepted:    267K
# Total Submissions: 423K
# Testcase Example:  "[\"ProductOfNumbers\",\"add\",\"add\",\"add\",\"add\",\"add\",\"getProduct\",\"getProduct\",\"getProduct\",\"add\",\"getProduct\"]"
#
# Design an algorithm that accepts a stream of integers and retrieves the
# product of the last k integers of the stream.
#
# Implement the ProductOfNumbers class:
#
# ProductOfNumbers() Initializes the object with an empty stream.
#
# void add(int num) Appends the integer num to the stream.
#
# int getProduct(int k) Returns the product of the last k numbers in the
# current list. You can assume that always the current list has at least k
# numbers.
#
# The test cases are generated so that, at any time, the product of any
# contiguous sequence of numbers will fit into a single 32-bit integer without
# overflowing.
#
# Example:
#
# Input
# ["ProductOfNumbers","add","add","add","add","add","getProduct","getProduct","getProduct","add","getProduct"]
# [[],[3],[0],[2],[5],[4],[2],[3],[4],[8],[2]]
#
# Output
# [null,null,null,null,null,null,20,40,0,null,32]
#
# Explanation
# ProductOfNumbers productOfNumbers = new ProductOfNumbers();
# productOfNumbers.add(3); // [3]
# productOfNumbers.add(0); // [3,0]
# productOfNumbers.add(2); // [3,0,2]
# productOfNumbers.add(5); // [3,0,2,5]
# productOfNumbers.add(4); // [3,0,2,5,4]
# productOfNumbers.getProduct(2); // return 20. The product of the last 2
# numbers is 5 * 4 = 20
# productOfNumbers.getProduct(3); // return 40. The product of the last 3
# numbers is 2 * 5 * 4 = 40
# productOfNumbers.getProduct(4); // return 0. The product of the last 4
# numbers is 0 * 2 * 5 * 4 = 0
# productOfNumbers.add(8); // [3,0,2,5,4,8]
# productOfNumbers.getProduct(2); // return 32. The product of the last 2
# numbers is 4 * 8 = 32
#
# Constraints:
#
# 0 <= num <= 100
#
# 1 <= k <= 4 * 10^4
#
# At most 4 * 10^4 calls will be made to add and getProduct.
#
# The product of the stream at any point in time will fit in a 32-bit integer.
#
# Follow-up: Can you implement both GetProduct and Add to work in O(1) time
# complexity instead of O(k) time complexity?
#

# @lc code=start

class ProductOfNumbers:
    def __init__(self):
        """
        Interview explanation:
        Maintain prefix products after the last zero. Product of last k is
        prefix[-1]//prefix[-1-k] when k fits in the current zero-free suffix.

        Algorithm:
        - pref=[1]; on add(0) reset pref=[1]; else append pref[-1]*num

        Complexity: O(1) init.
        """
        self.pref = [1]

    def add(self, num: int) -> None:
        """
        Interview explanation:
        Append num to the stream. Zero invalidates prior prefix products.

        Algorithm:
        - If num==0: pref=[1]; else pref.append(pref[-1]*num)

        Complexity: O(1) amortized.
        """
        if num == 0:
            self.pref = [1]
        else:
            self.pref.append(self.pref[-1] * num)

    def getProduct(self, k: int) -> int:
        """
        Interview explanation:
        Return product of last k numbers (guaranteed to exist). If a zero sits
        within those k, answer is 0.

        Algorithm:
        - If k >= len(pref): return 0; else return pref[-1]//pref[-1-k]

        Complexity: O(1).
        """
        if k >= len(self.pref):
            return 0
        return self.pref[-1] // self.pref[-1 - k]


# Your ProductOfNumbers object will be instantiated and called as such:
# obj = ProductOfNumbers()
# obj.add(num)
# param_2 = obj.getProduct(k)
# @lc code=end
