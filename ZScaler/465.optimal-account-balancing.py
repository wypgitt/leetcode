#
# @lc app=leetcode id=465 lang=python3
#
# [465] Optimal Account Balancing
#
# https://leetcode.com/problems/optimal-account-balancing/description/
#
# algorithms
# Hard (50.60%)
# Likes:    1535
# Dislikes: 164
# Total Accepted:    117.5K
# Total Submissions: 232.3K
# Testcase Example:  "[[0,1,10],[2,0,5]]"
#
#
# You are given an array of transactions transactions where
# transactions[i] = [from_i, to_i, amount_i] indicates that the person
# with ID = from_i gave amount_i $ to the person with ID = to_i.
#
# Return the minimum number of transactions required to settle the debt.
#
# Example 1:
#
# Input: transactions = [[0,1,10],[2,0,5]]
# Output: 2
# Explanation:
# Person #0 gave person #1 $10.
# Person #2 gave person #0 $5.
# Two transactions are needed. One way to settle the debt is person #1
# pays person #0 and #2 $5 each.
#
# Example 2:
#
# Input: transactions = [[0,1,10],[1,0,1],[1,2,5],[2,0,5]]
# Output: 1
# Explanation:
# Person #0 gave person #1 $10.
# Person #1 gave person #0 $1.
# Person #1 gave person #2 $5.
# Person #2 gave person #0 $5.
# Therefore, person #1 only need to give person #0 $4, and all debt is
# settled.
#
# Constraints:
#
# 1 <= transactions.length <= 8
#
# transactions[i].length == 3
#
# 0 <= from_i, to_i < 12
#
# from_i != to_i
#
# 1 <= amount_i <= 100
#
# @lc code=start
from typing import List


class Solution:
    def minTransfers(self, transactions: List[List[int]]) -> int:
        """
        Interview explanation:
        Premium. Net balance per person; drop zeros. Remaining debts must be
        settled with minimum transfers. Backtrack over debt list: for each
        unsettled i, try settling with later j of opposite sign; recurse.
        Optionally DP on subset masks for small n.

        Algorithm:
        - Compute net[person]; debts = non-zero nets.
        - DFS(start): skip zeros; for j > i with opposite sign, transfer
          debts[j]+=debts[i], recurse, backtrack; take min transfers.
        - Prune by only trying one direction / skip same-sign.

        Complexity: O(n!) worst-case backtrack (n = non-zero balances), O(n) space.
        """
        bal = {}
        for a, b, amt in transactions:
            bal[a] = bal.get(a, 0) - amt
            bal[b] = bal.get(b, 0) + amt
        debts = [v for v in bal.values() if v]
        n = len(debts)

        def dfs(i: int) -> int:
            while i < n and debts[i] == 0:
                i += 1
            if i == n:
                return 0
            ans = float("inf")
            for j in range(i + 1, n):
                if debts[i] * debts[j] < 0:
                    debts[j] += debts[i]
                    ans = min(ans, 1 + dfs(i + 1))
                    debts[j] -= debts[i]
                    if debts[j] + debts[i] == 0:
                        break
            return int(ans)

        return dfs(0)

    def minTransfers_dp(self, transactions: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate classic: subset DP. Max number of non-overlapping zero-sum
        subsets of the debt list; min transfers = n - that count (each clearable
        group of size k needs k-1 transfers).

        Algorithm:
        - debts = non-zero nets; summ[mask] = sum of selected debts.
        - groups[mask] = max zero-sum groups inside mask (via removing one
          element, and +1 when summ[mask]==0).
        - Return n - groups[(1<<n)-1].

        Complexity: O(n * 2^n) time, O(2^n) space.
        """
        bal = {}
        for a, b, amt in transactions:
            bal[a] = bal.get(a, 0) - amt
            bal[b] = bal.get(b, 0) + amt
        debts = [v for v in bal.values() if v]
        n = len(debts)
        if n == 0:
            return 0
        N = 1 << n
        summ = [0] * N
        for mask in range(1, N):
            b = (mask & -mask).bit_length() - 1
            summ[mask] = summ[mask ^ (1 << b)] + debts[b]
        # groups[mask] = max zero-sum parts in a partition of mask (mask sum must be 0)
        groups = [0] * N
        for mask in range(1, N):
            if summ[mask] != 0:
                continue
            sub = mask
            while sub:
                if summ[sub] == 0:
                    groups[mask] = max(groups[mask], groups[mask ^ sub] + 1)
                sub = (sub - 1) & mask
        return n - groups[N - 1]
# @lc code=end
