#
# @lc app=leetcode id=751 lang=python3
#
# [751] IP to CIDR
#
# https://leetcode.com/problems/ip-to-cidr/description/
#
# algorithms
# Medium (53.56%)
# Likes:    118
# Dislikes: 367
# Total Accepted:    39.9K
# Total Submissions: 74.5K
# Testcase Example:  '"255.0.0.7"\n10'
#
# An IP address is a formatted 32-bit unsigned integer where each group of 8
# bits is printed as a decimal number and the dot character '.' splits the
# groups.
# 
# 
# For example, the binary number 00001111 10001000 11111111 01101011 (spaces
# added for clarity) formatted as an IP address would be "15.136.255.107".
# 
# 
# A CIDR block is a format used to denote a specific set of IP addresses. It is
# a string consisting of a base IP address, followed by a slash, followed by a
# prefix length k. The addresses it covers are all the IPs whose first k bits
# are the same as the base IP address.
# 
# 
# For example, "123.45.67.89/20" is a CIDR block with a prefix length of 20.
# Any IP address whose binary representation matches 01111011 00101101 0100xxxx
# xxxxxxxx, where x can be either 0 or 1, is in the set covered by the CIDR
# block.
# 
# 
# You are given a start IP address ip and the number of IP addresses we need to
# cover n. Your goal is to use as few CIDR blocks as possible to cover all the
# IP addresses in the inclusive range [ip, ip + n - 1] exactly. No other IP
# addresses outside of the range should be covered.
# 
# Return the shortest list of CIDR blocks that covers the range of IP
# addresses. If there are multiple answers, return any of them.
# 
# 
# Example 1:
# 
# 
# Input: ip = "255.0.0.7", n = 10
# Output: ["255.0.0.7/32","255.0.0.8/29","255.0.0.16/32"]
# Explanation:
# The IP addresses that need to be covered are:
# - 255.0.0.7  -> 11111111 00000000 00000000 00000111
# - 255.0.0.8  -> 11111111 00000000 00000000 00001000
# - 255.0.0.9  -> 11111111 00000000 00000000 00001001
# - 255.0.0.10 -> 11111111 00000000 00000000 00001010
# - 255.0.0.11 -> 11111111 00000000 00000000 00001011
# - 255.0.0.12 -> 11111111 00000000 00000000 00001100
# - 255.0.0.13 -> 11111111 00000000 00000000 00001101
# - 255.0.0.14 -> 11111111 00000000 00000000 00001110
# - 255.0.0.15 -> 11111111 00000000 00000000 00001111
# - 255.0.0.16 -> 11111111 00000000 00000000 00010000
# The CIDR block "255.0.0.7/32" covers the first address.
# The CIDR block "255.0.0.8/29" covers the middle 8 addresses (binary format of
# 11111111 00000000 00000000 00001xxx).
# The CIDR block "255.0.0.16/32" covers the last address.
# Note that while the CIDR block "255.0.0.0/28" does cover all the addresses,
# it also includes addresses outside of the range, so we cannot use it.
# 
# 
# Example 2:
# 
# 
# Input: ip = "117.145.102.62", n = 8
# Output: ["117.145.102.62/31","117.145.102.64/30","117.145.102.68/31"]
# 
# 
# 
# Constraints:
# 
# 
# 7 <= ip.length <= 15
# ip is a valid IPv4 on the form "a.b.c.d" where a, b, c, and d are integers in
# the range [0, 255].
# 1 <= n <= 1000
# Every implied address ip + x (for x < n) will be a valid IPv4 address.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def ipToCIDR(self, ip: str, n: int) -> List[str]:
        def ip_to_int(s: str) -> int:
            value = 0
            for part in map(int, s.split('.')):
                value = value * 256 + part
            return value

        def int_to_ip(x: int) -> str:
            return '.'.join(str((x >> shift) & 255) for shift in (24, 16, 8, 0))

        start = ip_to_int(ip)
        ans = []
        while n > 0:
            lowbit = start & -start
            if lowbit == 0:
                lowbit = 1 << 32
            block = lowbit
            while block > n:
                block >>= 1
            prefix = 32 - (block.bit_length() - 1)
            ans.append(f"{int_to_ip(start)}/{prefix}")
            start += block
            n -= block
        return ans
# @lc code=end

"""
Interview explanation:
Represent IP addresses as 32-bit integers. At each step choose the largest power-of-two CIDR block that starts at the current address and does not exceed the remaining count. Alignment requires the block size to be no larger than the current address lowbit.

Data structure: integer arithmetic replaces string-heavy IP manipulation.

Edge cases: address 0 has lowbit 0, so treat it as aligned to the full 2^32 range. If the aligned block is too large for n, halve it until it fits.

Complexity: each emitted block is one loop iteration, and at most 32 block-size reductions occur per iteration. Space is O(number of CIDR blocks) for output.
"""
