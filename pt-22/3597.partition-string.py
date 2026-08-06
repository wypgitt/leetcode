#
# @lc app=leetcode id=3597 lang=python3
#
# [3597] Partition String 
#
# https://leetcode.com/problems/partition-string/description/
#
# algorithms
# Medium (59.49%)
# Likes:    75
# Dislikes: 8
# Total Accepted:    40.5K
# Total Submissions: 68K
# Testcase Example:  "\"abbccccd\""
#
#
# Given a string s, partition it into unique segments according to the
# following procedure:
#
# Start building a segment beginning at index 0.
#
# Continue extending the current segment character by character until the
# current segment has not been seen before.
#
# Once the segment is unique, add it to your list of segments, mark it as
# seen, and begin a new segment from the next index.
#
# Repeat until you reach the end of s.
#
# Return an array of strings segments, where segments[i] is the i^th
# segment created.
#
# Example 1:
#
# Input: s = "abbccccd"
#
# Output: ["a","b","bc","c","cc","d"]
#
# Explanation:
#
#                         Index
#                         Segment After Adding
#                         Seen Segments
#                         Current Segment Seen Before?
#                         New Segment
#                         Updated Seen Segments
#
#                         0
#                         "a"
#                         []
#                         No
#                         ""
#                         ["a"]
#
#                         1
#                         "b"
#                         ["a"]
#                         No
#                         ""
#                         ["a", "b"]
#
#                         2
#                         "b"
#                         ["a", "b"]
#                         Yes
#                         "b"
#                         ["a", "b"]
#
#                         3
#                         "bc"
#                         ["a", "b"]
#                         No
#                         ""
#                         ["a", "b", "bc"]
#
#                         4
#                         "c"
#                         ["a", "b", "bc"]
#                         No
#                         ""
#                         ["a", "b", "bc", "c"]
#
#                         5
#                         "c"
#                         ["a", "b", "bc", "c"]
#                         Yes
#                         "c"
#                         ["a", "b", "bc", "c"]
#
#                         6
#                         "cc"
#                         ["a", "b", "bc", "c"]
#                         No
#                         ""
#                         ["a", "b", "bc", "c", "cc"]
#
#                         7
#                         "d"
#                         ["a", "b", "bc", "c", "cc"]
#                         No
#                         ""
#                         ["a", "b", "bc", "c", "cc", "d"]
#
# Hence, the final output is ["a", "b", "bc", "c", "cc", "d"].
#
# Example 2:
#
# Input: s = "aaaa"
#
# Output: ["a","aa"]
#
# Explanation:
#
#                         Index
#                         Segment After Adding
#                         Seen Segments
#                         Current Segment Seen Before?
#                         New Segment
#                         Updated Seen Segments
#
#                         0
#                         "a"
#                         []
#                         No
#                         ""
#                         ["a"]
#
#                         1
#                         "a"
#                         ["a"]
#                         Yes
#                         "a"
#                         ["a"]
#
#                         2
#                         "aa"
#                         ["a"]
#                         No
#                         ""
#                         ["a", "aa"]
#
#                         3
#                         "a"
#                         ["a", "aa"]
#                         Yes
#                         "a"
#                         ["a", "aa"]
#
# Hence, the final output is ["a", "aa"].
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s contains only lowercase English letters.
#

# @lc code=start

from typing import List


class Solution:
    def partitionString(self, s: str) -> List[str]:
        """
        Interview explanation:
        Greedily grow the current segment until it is unseen, then cut and mark
        it seen. A trailing segment that never becomes unique is dropped.

        Algorithm:
        - Maintain a set of seen segments and the current buffer.
        - On each char, append; if buffer ∉ seen, emit it, add to seen, clear.

        Complexity: O(n · L) time for hashing (L segment length), O(n) space.
        """
        seen: set[str] = set()
        ans: List[str] = []
        cur: List[str] = []
        for ch in s:
            cur.append(ch)
            seg = "".join(cur)
            if seg not in seen:
                seen.add(seg)
                ans.append(seg)
                cur.clear()
        return ans

    def partitionString_trie(self, s: str) -> List[str]:
        """
        Interview explanation:
        Alternate: trie marks seen prefixes; creating a new edge ends a segment.

        Algorithm:
        - Walk/create trie nodes per char; on a new child, emit segment and reset.

        Complexity: O(n) time, O(n) space.
        """
        root: dict = {}
        node = root
        ans: List[str] = []
        cur: List[str] = []
        for ch in s:
            cur.append(ch)
            if ch not in node:
                node[ch] = {}
                ans.append("".join(cur))
                cur.clear()
                node = root
            else:
                node = node[ch]
        return ans
# @lc code=end
