#
# @lc app=leetcode id=193 lang=python3
#
# [193] Valid Phone Numbers
#
# https://leetcode.com/problems/valid-phone-numbers/description/
#
# algorithms
# Easy (30.45%)
# Likes:    488
# Dislikes: 983
# Total Accepted:    140K
# Total Submissions: 461K
# Testcase Example:  "0"
#
# Given a text file file.txt that contains a list of phone numbers (one per
# line), write a one-liner bash script to print all valid phone numbers.
#
# You may assume that a valid phone number must appear in one of the following
# two formats: (xxx) xxx-xxxx or xxx-xxx-xxxx. (x means a digit)
#
# You may also assume each line in the text file must not contain leading or
# trailing white spaces.
#
# Example:
#
# Assume that file.txt has the following content:
#
# 987-123-4567
# 123 456 7890
# (123) 456-7890
#
# Your script should output the following valid phone numbers:
#
# 987-123-4567
# (123) 456-7890
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Filter lines of file.txt that exactly match one of two phone formats
        using an extended regex anchored to start and end of line.

        Algorithm:
        - grep -E with alternation:
          (xxx) xxx-xxxx  OR  xxx-xxx-xxxx
          where x is [0-9], with ^...$ so the whole line must match.

        Complexity: O(L) over total file length; one pass streaming filter.

        Alternate:
        - awk with the same regex: awk '/^(...)$/' file.txt
        """
        return self.bash

    # LeetCode Bash — one-liner for file.txt (grep or awk)
    bash = r"""grep -E '^(\([0-9]{3}\) [0-9]{3}-[0-9]{4}|[0-9]{3}-[0-9]{3}-[0-9]{4})$' file.txt"""
# @lc code=end
