#
# @lc app=leetcode id=1233 lang=python3
#
# [1233] Remove Sub-Folders from the Filesystem
#
# https://leetcode.com/problems/remove-sub-folders-from-the-filesystem/description/
#
# algorithms
# Medium (78.60%)
# Likes:    1663
# Dislikes: 232
# Total Accepted:    266.1K
# Total Submissions: 338.6K
# Testcase Example:  '["/a","/a/b","/c/d","/c/d/e","/c/f"]'
#
# Given a list of folders folder, return the folders after removing all
# sub-folders in those folders. You may return the answer in any order.
# 
# If a folder[i] is located within another folder[j], it is called a sub-folder
# of it. A sub-folder of folder[j] must start with folder[j], followed by a
# "/". For example, "/a/b" is a sub-folder of "/a", but "/b" is not a
# sub-folder of "/a/b/c".
# 
# The format of a path is one or more concatenated strings of the form: '/'
# followed by one or more lowercase English letters.
# 
# 
# For example, "/leetcode" and "/leetcode/problems" are valid paths while an
# empty string and "/" are not.
# 
# 
# 
# Example 1:
# 
# 
# Input: folder = ["/a","/a/b","/c/d","/c/d/e","/c/f"]
# Output: ["/a","/c/d","/c/f"]
# Explanation: Folders "/a/b" is a subfolder of "/a" and "/c/d/e" is inside of
# folder "/c/d" in our filesystem.
# 
# 
# Example 2:
# 
# 
# Input: folder = ["/a","/a/b/c","/a/b/d"]
# Output: ["/a"]
# Explanation: Folders "/a/b/c" and "/a/b/d" will be removed because they are
# subfolders of "/a".
# 
# 
# Example 3:
# 
# 
# Input: folder = ["/a/b/c","/a/b/ca","/a/b/d"]
# Output: ["/a/b/c","/a/b/ca","/a/b/d"]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= folder.length <= 4 * 10^4
# 2 <= folder[i].length <= 100
# folder[i] contains only lowercase letters and '/'.
# folder[i] always starts with the character '/'.
# Each folder name is unique.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def removeSubfolders(self, folder: List[str]) -> List[str]:
        folder.sort()
        roots = []

        for path in folder:
            if not roots or not path.startswith(roots[-1] + "/"):
                roots.append(path)

        return roots
# @lc code=end

# Explanation
# -----------
# Sort folders lexicographically. A parent folder always appears before its
# subfolders because "/a" comes before "/a/b". Keep the latest accepted root;
# a new path is a subfolder exactly when it starts with root + "/".
#
# The slash check is important: "/a/b" is under "/a", but "/ab" is not.
#
# Sorting is the useful structure here because it groups each parent directly
# before all of its descendants, so no trie is needed.
#
# Edge cases: sibling folders with common text prefixes; duplicated-looking
# nested chains; root list initially empty.
#
# Time complexity: O(n log n * L) for sorting/comparisons.
# Space complexity: O(n) for the result.
