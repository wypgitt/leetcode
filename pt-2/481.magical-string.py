#
# @lc app=leetcode id=481 lang=python3
#
# [481] Magical String
#
# https://leetcode.com/problems/magical-string/description/
#
# algorithms
# Medium (55.13%)
# Likes:    383
# Dislikes: 1425
# Total Accepted:    56.7K
# Total Submissions: 102.8K
# Testcase Example:  '6'
#
# A magical string s consists of only '1' and '2' and obeys the following
# rule:
# 
# 
# Concatenating the sequence of lengths of its consecutive groups of identical
# characters '1' and '2' generates the string s itself.
# 
# 
# The first few elements of s is s = "1221121221221121122……". If we group the
# consecutive 1's and 2's in s, it will be "1 22 11 2 1 22 1 22 11 2 11 22
# ......" and counting the occurrences of 1's or 2's in each group yields the
# sequence "1 2 2 1 1 2 1 2 2 1 2 2 ......".
# 
# You can see that concatenating the occurrence sequence gives us s itself.
# 
# Given an integer n, return the number of 1's in the first n number in the
# magical string s.
# 
# 
# Example 1:
# 
# 
# Input: n = 6
# Output: 3
# Explanation: The first 6 elements of magical string s is "122112" and it
# contains three 1's, so return 3.
# 
# 
# Example 2:
# 
# 
# Input: n = 1
# Output: 1
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 10^5
# 
# 
#

# @lc code=start
class Solution:
    def magicalString(self, n: int) -> int:
        if n <= 0:
            return 0
        s = [1, 2, 2]
        if n <= 3:
            return s[:n].count(1)

        read = 2
        next_num = 1
        ones = 1
        while len(s) < n:
            repeat = s[read]
            for _ in range(repeat):
                if len(s) == n:
                    break
                s.append(next_num)
                if next_num == 1:
                    ones += 1
            next_num = 3 - next_num
            read += 1
        return ones
# @lc code=end

"""
Interview explanation:
The magical string describes its own run lengths. Start with the known prefix 122. A read pointer tells how many copies of the next digit to append; the next digit alternates between 1 and 2.

Data structure: a dynamic list is needed because generated values become future run lengths.

Edge cases: n <= 3 is answered from the initial prefix; the append loop stops exactly at n so extra generated values are not counted.

Complexity: O(n) time to generate the prefix of length n and O(n) space for the string.
"""
