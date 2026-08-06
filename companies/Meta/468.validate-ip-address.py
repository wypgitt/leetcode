#
# @lc app=leetcode id=468 lang=python3
#
# [468] Validate IP Address
#
# https://leetcode.com/problems/validate-ip-address/description/
#
# algorithms
# Medium (28.44%)
# Likes:    1129
# Dislikes: 2746
# Total Accepted:    205K
# Total Submissions: 723K
# Testcase Example:  "\"172.16.254.1\""
#
# Given a string queryIP, return "IPv4" if IP is a valid IPv4 address, "IPv6"
# if IP is a valid IPv6 address or "Neither" if IP is not a correct IP of any
# type.
#
# A valid IPv4 address is an IP in the form "x_1.x_2.x_3.x_4" where 0 <= x_i <=
# 255 and x_i cannot contain leading zeros. For example, "192.168.1.1" and
# "192.168.1.0" are valid IPv4 addresses while "192.168.01.1", "192.168.1.00",
# and "192.168@1.1" are invalid IPv4 addresses.
#
# A valid IPv6 address is an IP in the form "x_1:x_2:x_3:x_4:x_5:x_6:x_7:x_8"
# where:
#
# 1 <= x_i.length <= 4
#
# x_i is a hexadecimal string which may contain digits, lowercase English
# letter ('a' to 'f') and upper-case English letters ('A' to 'F').
#
# Leading zeros are allowed in x_i.
#
# For example, "2001:0db8:85a3:0000:0000:8a2e:0370:7334" and
# "2001:db8:85a3:0:0:8A2E:0370:7334" are valid IPv6 addresses, while
# "2001:0db8:85a3::8A2E:037j:7334" and
# "02001:0db8:85a3:0000:0000:8a2e:0370:7334" are invalid IPv6 addresses.
#
# Example 1:
#
# Input: queryIP = "172.16.254.1"
# Output: "IPv4"
# Explanation: This is a valid IPv4 address, return "IPv4".
#
# Example 2:
#
# Input: queryIP = "2001:0db8:85a3:0:0:8A2E:0370:7334"
# Output: "IPv6"
# Explanation: This is a valid IPv6 address, return "IPv6".
#
# Example 3:
#
# Input: queryIP = "256.256.256.256"
# Output: "Neither"
# Explanation: This is neither a IPv4 address nor a IPv6 address.
#
# Constraints:
#
# queryIP consists only of English letters, digits and the characters '.' and
# ':'.
#

# @lc code=start
class Solution:
    def validIPAddress(self, queryIP: str) -> str:
        """
        Interview explanation:
        Classify IPv4 / IPv6 / Neither by splitting on '.' or ':' and
        validating each chunk against the respective rules (no leading zeros
        for IPv4; 1–4 hex digits for IPv6).

        Algorithm:
        - If '.' in query: 4 chunks, each 0–255, digits only, no leading zero
          unless "0".
        - Elif ':' in query: 8 chunks, each 1–4 hex chars.
        - Else Neither.

        Complexity: O(n) time, O(1) space.
        """
        if queryIP.count(".") == 3:
            parts = queryIP.split(".")
            if len(parts) != 4:
                return "Neither"
            for p in parts:
                if not p or not p.isdigit() or (p[0] == "0" and len(p) > 1):
                    return "Neither"
                if not 0 <= int(p) <= 255:
                    return "Neither"
            return "IPv4"
        if queryIP.count(":") == 7:
            parts = queryIP.split(":")
            if len(parts) != 8:
                return "Neither"
            hexdigits = set("0123456789abcdefABCDEF")
            for p in parts:
                if not 1 <= len(p) <= 4 or any(c not in hexdigits for c in p):
                    return "Neither"
            return "IPv6"
        return "Neither"
# @lc code=end
