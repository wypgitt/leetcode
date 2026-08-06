#
# @lc app=leetcode id=777 lang=python3
#
# [777] Swap Adjacent in LR String
#
# https://leetcode.com/problems/swap-adjacent-in-lr-string/description/
#
# algorithms
# Medium (38.09%)
# Likes:    1348
# Dislikes: 956
# Total Accepted:    98.6K
# Total Submissions: 258.7K
# Testcase Example:  '"RXXLRXRXL"\n"XRLXXRRLX"'
#
# In a string composed of 'L', 'R', and 'X' characters, like "RXXLRXRXL", a
# move consists of either replacing one occurrence of "XL" with "LX", or
# replacing one occurrence of "RX" with "XR". Given the starting string start
# and the ending string result, return True if and only if there exists a
# sequence of moves to transform start to result.
# 
# 
# Example 1:
# 
# 
# Input: start = "RXXLRXRXL", result = "XRLXXRRLX"
# Output: true
# Explanation: We can transform start to result following these steps:
# RXXLRXRXL ->
# XRXLRXRXL ->
# XRLXRXRXL ->
# XRLXXRRXL ->
# XRLXXRRLX
# 
# 
# Example 2:
# 
# 
# Input: start = "X", result = "L"
# Output: false
# 
# 
# 
# Constraints:
# 
# 
# 1 <= start.length <= 10^4
# start.length == result.length
# Both start and result will only consist of characters in 'L', 'R', and 'X'.
# 
# 
#

# @lc code=start
class Solution:
    def canTransform(self, start: str, result: str) -> bool:
        if start.replace('X', '') != result.replace('X', ''):
            return False
        i = j = 0
        n = len(start)
        while i < n and j < n:
            while i < n and start[i] == 'X':
                i += 1
            while j < n and result[j] == 'X':
                j += 1
            if i == n or j == n:
                break
            if start[i] == 'L' and i < j:
                return False
            if start[i] == 'R' and i > j:
                return False
            i += 1
            j += 1
        return True
# @lc code=end

"""
Interview explanation:
Removing X characters, the sequence of L and R pieces can never change. The only remaining question is movement direction: L can move only left through XL -> LX, so its final index cannot be to the right; R can move only right through RX -> XR, so its final index cannot be to the left.

Data structure: two pointers scan the non-X characters and compare their positions.

Edge cases: mismatched non-X sequences fail immediately. Equal strings and strings with only X pass.

Complexity: O(n) time and O(n) temporary space from replace; this can be O(1) extra if the non-X sequence check is folded into the pointer scan.
"""
