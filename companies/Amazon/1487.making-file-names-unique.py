#
# @lc app=leetcode id=1487 lang=python3
#
# [1487] Making File Names Unique
#
# https://leetcode.com/problems/making-file-names-unique/description/
#
# algorithms
# Medium (38.84%)
# Likes:    467
# Dislikes: 743
# Total Accepted:    40.7K
# Total Submissions: 105K
# Testcase Example:  "[\"pes\",\"fifa\",\"gta\",\"pes(2019)\"]"
#
# Given an array of strings names of size n. You will create n folders in your
# file system such that, at the i^th minute, you will create a folder with the
# name names[i].
#
# Since two files cannot have the same name, if you enter a folder name that
# was previously used, the system will have a suffix addition to its name in
# the form of (k), where, k is the smallest positive integer such that the
# obtained name remains unique.
#
# Return an array of strings of length n where ans[i] is the actual name the
# system will assign to the i^th folder when you create it.
#
# Example 1:
#
# Input: names = ["pes","fifa","gta","pes(2019)"]
# Output: ["pes","fifa","gta","pes(2019)"]
# Explanation: Let's see how the file system creates folder names:
# "pes" --> not assigned before, remains "pes"
# "fifa" --> not assigned before, remains "fifa"
# "gta" --> not assigned before, remains "gta"
# "pes(2019)" --> not assigned before, remains "pes(2019)"
#
# Example 2:
#
# Input: names = ["gta","gta(1)","gta","avalon"]
# Output: ["gta","gta(1)","gta(2)","avalon"]
# Explanation: Let's see how the file system creates folder names:
# "gta" --> not assigned before, remains "gta"
# "gta(1)" --> not assigned before, remains "gta(1)"
# "gta" --> the name is reserved, system adds (k), since "gta(1)" is also
# reserved, systems put k = 2. it becomes "gta(2)"
# "avalon" --> not assigned before, remains "avalon"
#
# Example 3:
#
# Input: names =
# ["onepiece","onepiece(1)","onepiece(2)","onepiece(3)","onepiece"]
# Output: ["onepiece","onepiece(1)","onepiece(2)","onepiece(3)","onepiece(4)"]
# Explanation: When the last folder is created, the smallest positive valid k
# is 4, and it becomes "onepiece(4)".
#
# Constraints:
#
# 1 <= names.length <= 5 * 10^4
#
# 1 <= names[i].length <= 20
#
# names[i] consists of lowercase English letters, digits, and/or round
# brackets.
#

# @lc code=start
from typing import List


class Solution:
    def getFolderNames(self, names: List[str]) -> List[str]:
        """
        Interview explanation:
        Assign unique folder names: if name exists, try name(k) with smallest
        positive k. Track last used suffix per base to avoid rescanning.

        Algorithm:
        - used map name→next_k; for each name, while taken increment k from
          saved next; mark final name used.

        Complexity: O(total length + assigned suffixes) amortized.
        """
        used = {}
        ans = []
        for name in names:
            if name not in used:
                ans.append(name)
                used[name] = 1
            else:
                k = used[name]
                while f"{name}({k})" in used:
                    k += 1
                new = f"{name}({k})"
                ans.append(new)
                used[name] = k + 1
                used[new] = 1
        return ans
# @lc code=end
