#
# @lc app=leetcode id=1169 lang=python3
#
# [1169] Invalid Transactions
#
# https://leetcode.com/problems/invalid-transactions/description/
#
# algorithms
# Medium (32.46%)
# Likes:    624
# Dislikes: 2443
# Total Accepted:    118K
# Total Submissions: 365K
# Testcase Example:  "[\"alice,20,800,mtv\",\"alice,50,100,beijing\"]"
#
# A transaction is possibly invalid if:
#
# the amount exceeds $1000, or;
#
# if it occurs within (and including) 60 minutes of another transaction with
# the same name in a different city.
#
# You are given an array of strings transaction where transactions[i] consists
# of comma-separated values representing the name, time (in minutes), amount,
# and city of the transaction.
#
# Return a list of transactions that are possibly invalid. You may return the
# answer in any order.
#
# Example 1:
#
# Input: transactions = ["alice,20,800,mtv","alice,50,100,beijing"]
# Output: ["alice,20,800,mtv","alice,50,100,beijing"]
# Explanation: The first transaction is invalid because the second transaction
# occurs within a difference of 60 minutes, have the same name and is in a
# different city. Similarly the second one is invalid too.
#
# Example 2:
#
# Input: transactions = ["alice,20,800,mtv","alice,50,1200,mtv"]
# Output: ["alice,50,1200,mtv"]
#
# Example 3:
#
# Input: transactions = ["alice,20,800,mtv","bob,50,1200,mtv"]
# Output: ["bob,50,1200,mtv"]
#
# Constraints:
#
# transactions.length <= 1000
#
# Each transactions[i] takes the form "{name},{time},{amount},{city}"
#
# Each {name} and {city} consist of lowercase English letters, and have lengths
# between 1 and 10.
#
# Each {time} consist of digits, and represent an integer between 0 and 1000.
#
# Each {amount} consist of digits, and represent an integer between 0 and 2000.
#

# @lc code=start

from typing import List


class Solution:
    def invalidTransactions(self, transactions: List[str]) -> List[str]:
        """
        Interview explanation:
        A transaction is invalid if amount > 1000, or same name appears in a
        different city within 60 minutes. Parse all, then check each against
        others with the same name (n <= 1000 so O(n^2) is fine).

        Algorithm:
        - Parse to (name, time, amount, city, raw).
        - For each i: if amount > 1000 mark invalid; else scan same-name j with
          |time_i-time_j| <= 60 and city differs → mark both invalid.
        - Collect marked raw strings.

        Complexity: O(n^2) time, O(n) space.
        """
        parsed = []
        for t in transactions:
            name, time, amount, city = t.split(',')
            parsed.append((name, int(time), int(amount), city, t))

        n = len(parsed)
        bad = [False] * n
        for i in range(n):
            name_i, time_i, amount_i, city_i, _ = parsed[i]
            if amount_i > 1000:
                bad[i] = True
            for j in range(n):
                if i == j:
                    continue
                name_j, time_j, _, city_j, _ = parsed[j]
                if name_i == name_j and city_i != city_j and abs(time_i - time_j) <= 60:
                    bad[i] = True
                    break
        return [parsed[i][4] for i in range(n) if bad[i]]
# @lc code=end
