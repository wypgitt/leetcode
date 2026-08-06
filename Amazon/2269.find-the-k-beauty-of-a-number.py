#
# @lc app=leetcode id=2269 lang=python3
#
# [2269] Find the K-Beauty of a Number
#
# https://leetcode.com/problems/find-the-k-beauty-of-a-number/description/
#
# algorithms
# Easy (63.68%)
# Likes:    747
# Dislikes: 47
# Total Accepted:    97.7K
# Total Submissions: 153.4K
# Testcase Example:  "240\n2"
#
# The k-beauty of an integer num is defined as the number of substrings of num
# when it is read as a string that meet the following conditions:
#
#
# It has a length of k.
#
#
# It is a divisor of num.
#
# Given integers num and k, return the k-beauty of num.
#
# Note:
#
#
# Leading zeros are allowed.
#
#
# 0 is not a divisor of any value.
#
# A substring is a contiguous sequence of characters in a string.
#
#
#
# Example 1:
#
# Input: num = 240, k = 2
# Output: 2
# Explanation: The following are the substrings of num of length k:
# - "24" from "240": 24 is a divisor of 240.
# - "40" from "240": 40 is a divisor of 240.
# Therefore, the k-beauty is 2.
#
# Example 2:
#
# Input: num = 430043, k = 2
# Output: 2
# Explanation: The following are the substrings of num of length k:
# - "43" from "430043": 43 is a divisor of 430043.
# - "30" from "430043": 30 is not a divisor of 430043.
# - "00" from "430043": 0 is not a divisor of 430043.
# - "04" from "430043": 4 is not a divisor of 430043.
# - "43" from "430043": 43 is a divisor of 430043.
# Therefore, the k-beauty is 2.
#
#
#
# Constraints:
#
#
# 1 <= num <= 10^9
#
#
# 1 <= k <= num.length (taking num as a string)
#

# @lc code=start
class Solution:
    def divisorSubstrings(self, num: int, k: int) -> int:
        """
        Interview explanation:
        k-beauty = count of k-digit substrings of num that evenly divide num
        (ignore 0 substrings).

        Algorithm:
        - Slide window of length k on digit string; check int(sub) | num.

        Complexity: O(d) time, O(d) space for digit string length d.
        """
        s = str(num)
        ans = 0
        for i in range(len(s) - k + 1):
            v = int(s[i : i + k])
            if v and num % v == 0:
                ans += 1
        return ans
# @lc code=end
