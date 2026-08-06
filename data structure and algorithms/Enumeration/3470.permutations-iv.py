#
# @lc app=leetcode id=3470 lang=python3
#
# [3470] Permutations IV
#
# https://leetcode.com/problems/permutations-iv/description/
#
# algorithms
# Hard (34.60%)
# Likes:    31
# Dislikes: 4
# Total Accepted:    4.6K
# Total Submissions: 13.2K
# Testcase Example:  "4\n6"
#
#
# Given two integers, n and k, an alternating permutation is a permutation
# of the first n positive integers such that no two adjacent elements are
# both odd or both even.
#
# Return the k-th alternating permutation sorted in lexicographical order.
# If there are fewer than k valid alternating permutations, return an
# empty list.
#
# Example 1:
#
# Input: n = 4, k = 6
#
# Output: [3,4,1,2]
#
# Explanation:
#
# The lexicographically-sorted alternating permutations of [1, 2, 3, 4]
# are:
#
# [1, 2, 3, 4]
#
# [1, 4, 3, 2]
#
# [2, 1, 4, 3]
#
# [2, 3, 4, 1]
#
# [3, 2, 1, 4]
#
# [3, 4, 1, 2] ← 6th permutation
#
# [4, 1, 2, 3]
#
# [4, 3, 2, 1]
#
# Since k = 6, we return [3, 4, 1, 2].
#
# Example 2:
#
# Input: n = 3, k = 2
#
# Output: [3,2,1]
#
# Explanation:
#
# The lexicographically-sorted alternating permutations of [1, 2, 3] are:
#
# [1, 2, 3]
#
# [3, 2, 1] ← 2nd permutation
#
# Since k = 2, we return [3, 2, 1].
#
# Example 3:
#
# Input: n = 2, k = 3
#
# Output: []
#
# Explanation:
#
# The lexicographically-sorted alternating permutations of [1, 2] are:
#
# [1, 2]
#
# [2, 1]
#
# There are only 2 alternating permutations, but k = 3, which is out of
# range. Thus, we return an empty list [].
#
# Constraints:
#
# 1 <= n <= 100
#
# 1 <= k <= 10^15
#

# @lc code=start
import math
from typing import List


class Solution:
    def permute(self, n: int, k: int) -> List[int]:
        """
        Interview explanation:
        Build the k-th lex alternating permutation digit by digit. At each
        position count how many completions each candidate starts.

        Algorithm:
        - Remaining odds/evens determine factorial product of free slots.
        - First position: if n odd must start odd; if n even any parity.
        - Later positions must flip parity from the previous choice.
        - Subtract block sizes from k until the correct digit is found.

        Complexity: O(n^2) time, O(n) space. Factorials handled by Python ints.
        """
        ans: List[int] = []
        # True means next required parity is odd (see number % 2 != flag).
        looking_odd_flag = True
        remaining = list(range(1, n + 1))

        for turn in range(n):
            rem_perm = math.factorial((n - 1 - turn) // 2) * math.factorial(
                (n - turn) // 2
            )
            found = False
            for index, number in enumerate(remaining):
                if number % 2 != looking_odd_flag and (turn > 0 or n % 2 == 1):
                    continue
                if k <= rem_perm:
                    ans.append(remaining.pop(index))
                    looking_odd_flag = ans[-1] % 2 == 0
                    found = True
                    break
                k -= rem_perm
            if not found:
                return []
        return ans
# @lc code=end

