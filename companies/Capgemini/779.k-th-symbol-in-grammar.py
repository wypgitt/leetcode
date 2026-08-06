#
# @lc app=leetcode id=779 lang=python3
#
# [779] K-th Symbol in Grammar
#
# https://leetcode.com/problems/k-th-symbol-in-grammar/description/
#
# algorithms
# Medium (48.57%)
# Likes:    4188
# Dislikes: 427
# Total Accepted:    267K
# Total Submissions: 550K
# Testcase Example:  "1"
#
# We build a table of n rows (1-indexed). We start by writing 0 in the 1^st
# row. Now in every subsequent row, we look at the previous row and replace
# each occurrence of 0 with 01, and each occurrence of 1 with 10.
#
# For example, for n = 3, the 1^st row is 0, the 2^nd row is 01, and the 3^rd
# row is 0110.
#
# Given two integer n and k, return the k^th (1-indexed) symbol in the n^th row
# of a table of n rows.
#
# Example 1:
#
# Input: n = 1, k = 1
# Output: 0
# Explanation: row 1: 0
#
# Example 2:
#
# Input: n = 2, k = 1
# Output: 0
# Explanation:
# row 1: 0
# row 2: 01
#
# Example 3:
#
# Input: n = 2, k = 2
# Output: 1
# Explanation:
# row 1: 0
# row 2: 01
#
# Constraints:
#
# 1 <= n <= 30
#
# 1 <= k <= 2^n - 1
#

# @lc code=start
class Solution:
    def kthGrammar(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Row builds by 0→01, 1→10. The k-th symbol (1-indexed) equals the parent
        in previous row at ceil(k/2), flipped if k is even (right child).
        Recurse until row 1.

        Algorithm:
        - If n == 1: return 0
        - parent = kthGrammar(n-1, (k+1)//2)
        - If k odd: same as parent; else 1 - parent

        Complexity: O(n) time, O(n) space (recursion).
        """
        if n == 1:
            return 0
        parent = self.kthGrammar(n - 1, (k + 1) // 2)
        # left child (odd k) keeps parent; right child flips
        return parent if k % 2 == 1 else 1 - parent

    def kthGrammar_bit(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Alternate classic: answer is parity of number of 1-bits in (k-1)
        (each flip corresponds to a right-child / set bit along the path).

        Algorithm:
        - return bin(k - 1).count("1") % 2

        Complexity: O(log k) time, O(1) space.
        """
        return bin(k - 1).count("1") % 2
# @lc code=end

