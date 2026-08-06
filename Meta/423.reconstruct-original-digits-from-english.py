#
# @lc app=leetcode id=423 lang=python3
#
# [423] Reconstruct Original Digits from English
#
# https://leetcode.com/problems/reconstruct-original-digits-from-english/description/
#
# algorithms
# Medium (52.87%)
# Likes:    895
# Dislikes: 2812
# Total Accepted:    100.2K
# Total Submissions: 189.6K
# Testcase Example:  '"owoztneoer"'
#
# Given a string s containing an out-of-order English representation of digits
# 0-9, return the digits in ascending order.
# 
# 
# Example 1:
# Input: s = "owoztneoer"
# Output: "012"
# Example 2:
# Input: s = "fviefuro"
# Output: "45"
# 
# 
# Constraints:
# 
# 
# 1 <= s.length <= 10^5
# s[i] is one of the characters
# ["e","g","f","i","h","o","n","s","r","u","t","w","v","x","z"].
# s is guaranteed to be valid.
# 
# 
#

# @lc code=start
from collections import Counter


class Solution:
    def originalDigits(self, s: str) -> str:
        count = Counter(s)
        digit = [0] * 10
        digit[0] = count['z']
        digit[2] = count['w']
        digit[4] = count['u']
        digit[6] = count['x']
        digit[8] = count['g']
        digit[3] = count['h'] - digit[8]
        digit[5] = count['f'] - digit[4]
        digit[7] = count['s'] - digit[6]
        digit[1] = count['o'] - digit[0] - digit[2] - digit[4]
        digit[9] = count['i'] - digit[5] - digit[6] - digit[8]
        return ''.join(str(i) * digit[i] for i in range(10))
# @lc code=end

"""
Interview explanation:
Use letters that uniquely identify digits: z->zero, w->two, u->four, x->six, g->eight. After removing those counts conceptually, other distinguishing letters reveal the remaining digits.

Data structure: Counter gives O(1) access to each character frequency.

Edge cases: duplicated digits are handled by multiplying the output digit string by its count. The final answer is sorted because the problem asks digits in ascending order.

Complexity: O(n) time to count letters and O(1) auxiliary space because the alphabet and digit set are fixed.
"""
