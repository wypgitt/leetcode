#
# @lc app=leetcode id=93 lang=python3
#
# [93] Restore IP Addresses
#
# https://leetcode.com/problems/restore-ip-addresses/description/
#
# algorithms
# Medium (55.93%)
# Likes:    5669
# Dislikes: 821
# Total Accepted:    628.2K
# Total Submissions: 1.1M
# Testcase Example:  '"25525511135"'
#
# A valid IP address consists of exactly four integers separated by single
# dots. Each integer is between 0 and 255 (inclusive) and cannot have leading
# zeros.
# 
# 
# For example, "0.1.2.201" and "192.168.1.1" are valid IP addresses, but
# "0.011.255.245", "192.168.1.312" and "192.168@1.1" are invalid IP
# addresses.
# 
# 
# Given a string s containing only digits, return all possible valid IP
# addresses that can be formed by inserting dots into s. You are not allowed to
# reorder or remove any digits in s. You may return the valid IP addresses in
# any order.
# 
# 
# Example 1:
# 
# 
# Input: s = "25525511135"
# Output: ["255.255.11.135","255.255.111.35"]
# 
# 
# Example 2:
# 
# 
# Input: s = "0000"
# Output: ["0.0.0.0"]
# 
# 
# Example 3:
# 
# 
# Input: s = "101023"
# Output: ["1.0.10.23","1.0.102.3","10.1.0.23","10.10.2.3","101.0.2.3"]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s.length <= 20
# s consists of digits only.
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def restoreIpAddresses(self, s: str) -> List[str]:
        """
        Interview explanation:
        An IP address has exactly four parts, each length 1 to 3 and value 0 to
        255. Backtracking tries each valid next part. Pruning by remaining length
        keeps the search small and makes the validity rules explicit.

        Edge cases and tests:
        - Length less than 4 or greater than 12 returns [].
        - Leading zero is allowed only for the single part '0'.
        - Segment values over 255 are invalid.

        Complexity: O(1) in practice because there are at most 3^4 segment
        choices; output size is bounded by a small constant.
        """
        ans = []
        path = []

        def valid(part: str) -> bool:
            return (part == '0' or not part.startswith('0')) and int(part) <= 255

        def dfs(index: int) -> None:
            parts_left = 4 - len(path)
            chars_left = len(s) - index
            if chars_left < parts_left or chars_left > parts_left * 3:
                return
            if len(path) == 4:
                if index == len(s):
                    ans.append('.'.join(path))
                return
            for end in range(index + 1, min(index + 4, len(s) + 1)):
                part = s[index:end]
                if valid(part):
                    path.append(part)
                    dfs(end)
                    path.pop()

        dfs(0)
        return ans
# @lc code=end


