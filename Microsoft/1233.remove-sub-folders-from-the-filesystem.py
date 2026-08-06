#
# @lc app=leetcode id=1233 lang=python3
#
# [1233] Remove Sub-Folders from the Filesystem
#
# https://leetcode.com/problems/remove-sub-folders-from-the-filesystem/description/
#
# algorithms
# Medium (78.6%)
# Likes:    1670
# Dislikes: 232
# Total Accepted:    269K
# Total Submissions: 342K
# Testcase Example:  "[\"/a\",\"/a/b\",\"/c/d\",\"/c/d/e\",\"/c/f\"]"
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
# For example, "/leetcode" and "/leetcode/problems" are valid paths while an
# empty string and "/" are not.
#
# Example 1:
#
# Input: folder = ["/a","/a/b","/c/d","/c/d/e","/c/f"]
# Output: ["/a","/c/d","/c/f"]
# Explanation: Folders "/a/b" is a subfolder of "/a" and "/c/d/e" is inside of
# folder "/c/d" in our filesystem.
#
# Example 2:
#
# Input: folder = ["/a","/a/b/c","/a/b/d"]
# Output: ["/a"]
# Explanation: Folders "/a/b/c" and "/a/b/d" will be removed because they are
# subfolders of "/a".
#
# Example 3:
#
# Input: folder = ["/a/b/c","/a/b/ca","/a/b/d"]
# Output: ["/a/b/c","/a/b/ca","/a/b/d"]
#
# Constraints:
#
# 1 <= folder.length <= 4 * 10^4
#
# 2 <= folder[i].length <= 100
#
# folder[i] contains only lowercase letters and '/'.
#
# folder[i] always starts with the character '/'.
#
# Each folder name is unique.
#


# @lc code=start
from typing import List

class Solution:
    def removeSubfolders(self, folder: List[str]) -> List[str]:
        """
        Interview explanation:
        Remove folders that are subfolders of another. Sort lexicographically;
        a folder is a subfolder of the last kept if it starts with last+'/'.

        Algorithm:
        - Sort folder; ans=[]; for f: if not ans or not f.startswith(ans[-1]+'/'): append

        Complexity: O(n log n * L) time.
        """
        folder.sort()
        ans = []
        for f in folder:
            if not ans or not f.startswith(ans[-1] + "/"):
                ans.append(f)
        return ans

    def removeSubfolders_trie(self, folder: List[str]) -> List[str]:
        """
        Interview explanation:
        Alternate: insert path segments into a trie; mark folder ends; collect
        paths that never pass through an earlier end marker.

        Algorithm:
        - Trie node dict; insert all; DFS collect until end flag

        Complexity: O(total chars) time/space.
        """
        trie = {}
        for f in folder:
            node = trie
            for part in f.split("/")[1:]:
                node = node.setdefault(part, {})
            node["#"] = True

        ans = []

        def dfs(node, path):
            if "#" in node:
                ans.append("/" + "/".join(path))
                return
            for k, child in node.items():
                if k != "#":
                    path.append(k)
                    dfs(child, path)
                    path.pop()

        dfs(trie, [])
        return ans
# @lc code=end
