#
# @lc app=leetcode id=386 lang=python3
#
# [386] Lexicographical Numbers
#
# https://leetcode.com/problems/lexicographical-numbers/description/
#
# algorithms
# Medium (76.23%)
# Likes:    3140
# Dislikes: 214
# Total Accepted:    386.3K
# Total Submissions: 506.7K
# Testcase Example:  '13'
#
# Given an integer n, return all the numbers in the range [1, n] sorted in
# lexicographical order.
# 
# You must write an algorithm that runs in O(n) time and uses O(1) extra
# space. 
# 
# 
# Example 1:
# Input: n = 13
# Output: [1,10,11,12,13,2,3,4,5,6,7,8,9]
# Example 2:
# Input: n = 2
# Output: [1,2]
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 5 * 10^4
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def lexicalOrder(self, n: int) -> List[int]:
        ans = []
        cur = 1
        for _ in range(n):
            ans.append(cur)
            if cur * 10 <= n:
                cur *= 10
            else:
                while cur % 10 == 9 or cur + 1 > n:
                    cur //= 10
                cur += 1
        return ans
# @lc code=end

"""
Interview explanation:
Lexicographic order is the preorder traversal of a 10-ary prefix tree whose nodes are number prefixes. From a number x, the next lexicographic number is x * 10 if that child exists. Otherwise, climb until we can move to the next sibling x + 1.

Data structure: no explicit trie is needed because integer arithmetic navigates the implicit prefix tree.

Edge cases: when a prefix ends in 9 or the next sibling would exceed n, we repeatedly climb to the parent prefix.

Complexity: exactly n numbers are emitted and each climb is amortized across the traversal, so time is O(n). The output uses O(n) space; extra working space is O(1).
"""
