#
# @lc app=leetcode id=860 lang=python3
#
# [860] Lemonade Change
#
# https://leetcode.com/problems/lemonade-change/description/
#
# algorithms
# Easy (59.36%)
# Likes:    3516
# Dislikes: 219
# Total Accepted:    640K
# Total Submissions: 1.1M
# Testcase Example:  "[5,5,5,10,20]"
#
# At a lemonade stand, each lemonade costs $5. Customers are standing in a
# queue to buy from you and order one at a time (in the order specified by
# bills). Each customer will only buy one lemonade and pay with either a $5,
# $10, or $20 bill. You must provide the correct change to each customer so
# that the net transaction is that the customer pays $5.
#
# Note that you do not have any change in hand at first.
#
# Given an integer array bills where bills[i] is the bill the i^th customer
# pays, return true if you can provide every customer with the correct change,
# or false otherwise.
#
# Example 1:
#
# Input: bills = [5,5,5,10,20]
# Output: true
# Explanation:
# From the first 3 customers, we collect three $5 bills in order.
# From the fourth customer, we collect a $10 bill and give back a $5.
# From the fifth customer, we give a $10 bill and a $5 bill.
# Since all customers got correct change, we output true.
#
# Example 2:
#
# Input: bills = [5,5,10,10,20]
# Output: false
# Explanation:
# From the first two customers in order, we collect two $5 bills.
# For the next two customers in order, we collect a $10 bill and give back a $5
# bill.
# For the last customer, we can not give the change of $15 back because we only
# have two $10 bills.
# Since not every customer received the correct change, the answer is false.
#
# Constraints:
#
# 1 <= bills.length <= 10^5
#
# bills[i] is either 5, 10, or 20.
#

# @lc code=start

from typing import List


class Solution:
    def lemonadeChange(self, bills: List[int]) -> bool:
        """
        Interview explanation:
        Lemonade costs 5; bills are 5/10/20. Greedy: keep counts of 5s and 10s;
        for 10 give one 5; for 20 prefer 10+5 else three 5s.

        Algorithm:
        - five=ten=0; process bills; fail if cannot make change.

        Complexity: O(n) time, O(1) space.
        """
        five = ten = 0
        for b in bills:
            if b == 5:
                five += 1
            elif b == 10:
                if five == 0:
                    return False
                five -= 1
                ten += 1
            else:  # 20
                if ten and five:
                    ten -= 1
                    five -= 1
                elif five >= 3:
                    five -= 3
                else:
                    return False
        return True
# @lc code=end
