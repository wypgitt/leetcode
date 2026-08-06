#
# @lc app=leetcode id=1108 lang=python3
#
# [1108] Defanging an IP Address
#
# https://leetcode.com/problems/defanging-an-ip-address/description/
#
# algorithms
# Easy (90.12%)
# Likes:    2388
# Dislikes: 1793
# Total Accepted:    889K
# Total Submissions: 986K
# Testcase Example:  "\"1.1.1.1\""
#
# Given a valid (IPv4) IP address, return a defanged version of that IP
# address.
#
# A defanged IP address replaces every period "." with "[.]".
#
# Example 1:
#
# Input: address = "1.1.1.1"
# Output: "1[.]1[.]1[.]1"
#
# Example 2:
#
# Input: address = "255.100.50.0"
# Output: "255[.]100[.]50[.]0"
#
# Constraints:
#
# The given address is a valid IPv4 address.
#

# @lc code=start
class Solution:
    def defangIPaddr(self, address: str) -> str:
        """
        Interview explanation:
        Replace every '.' with '[.]' in a valid IPv4 string.

        Algorithm:
        - return address.replace('.', '[.]')
        - Alternate: join octets with '[.]'.

        Complexity: O(n) time/space.
        """
        return address.replace(".", "[.]")

    def defangIPaddr_join(self, address: str) -> str:
        """
        Interview explanation:
        Alternate: split on '.' and join with '[.]'.

        Algorithm:
        - '[.]'.join(address.split('.'))

        Complexity: O(n) time/space.
        """
        return "[.]".join(address.split("."))
# @lc code=end
