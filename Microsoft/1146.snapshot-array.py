#
# @lc app=leetcode id=1146 lang=python3
#
# [1146] Snapshot Array
#
# https://leetcode.com/problems/snapshot-array/description/
#
# algorithms
# Medium (36.79%)
# Likes:    3943
# Dislikes: 544
# Total Accepted:    289K
# Total Submissions: 784K
# Testcase Example:  "[\"SnapshotArray\",\"set\",\"snap\",\"set\",\"get\"]"
#
# Implement a SnapshotArray that supports the following interface:
#
# SnapshotArray(int length) initializes an array-like data structure with the
# given length. Initially, each element equals 0.
#
# void set(index, val) sets the element at the given index to be equal to val.
#
# int snap() takes a snapshot of the array and returns the snap_id: the total
# number of times we called snap() minus 1.
#
# int get(index, snap_id) returns the value at the given index, at the time we
# took the snapshot with the given snap_id
#
# Example 1:
#
# Input: ["SnapshotArray","set","snap","set","get"]
# [[3],[0,5],[],[0,6],[0,0]]
# Output: [null,null,0,null,5]
# Explanation:
# SnapshotArray snapshotArr = new SnapshotArray(3); // set the length to be 3
# snapshotArr.set(0,5); // Set array[0] = 5
# snapshotArr.snap(); // Take a snapshot, return snap_id = 0
# snapshotArr.set(0,6);
# snapshotArr.get(0,0); // Get the value of array[0] with snap_id = 0, return 5
#
# Constraints:
#
# 1 <= length <= 5 * 10^4
#
# 0 <= index < length
#
# 0 <= val <= 10^9
#
# 0 <= snap_id < (the total number of times we call snap())
#
# At most 5 * 10^4 calls will be made to set, snap, and get.
#

# @lc code=start
from typing import List
import bisect


class SnapshotArray:
    def __init__(self, length: int):
        """
        Interview explanation:
        Array with set/snap/get-at-snap. Store (snap_id, value) history per
        index; binary search on snap_id for get. Avoid full copies.

        Algorithm:
        - history[i] = list of (snap_id, val); snap_id counter starts at 0.

        Complexity: O(length) init space for empty histories.
        """
        self.snap_id = 0
        self.hist: List[List[List[int]]] = [[[0, 0]] for _ in range(length)]

    def set(self, index: int, val: int) -> None:
        """
        Interview explanation:
        Record value for current snap_id at index; overwrite if same snap already set.

        Algorithm:
        - If last history entry has current snap_id, update val; else append.

        Complexity: O(1) amortized.
        """
        h = self.hist[index]
        if h[-1][0] == self.snap_id:
            h[-1][1] = val
        else:
            h.append([self.snap_id, val])

    def snap(self) -> int:
        """
        Interview explanation:
        Advance snapshot counter and return previous id.

        Algorithm:
        - Return snap_id then increment.

        Complexity: O(1).
        """
        self.snap_id += 1
        return self.snap_id - 1

    def get(self, index: int, snap_id: int) -> int:
        """
        Interview explanation:
        Value at index as of snap_id: latest history entry with id <= snap_id.

        Algorithm:
        - bisect_right on snap ids; take previous entry's value.

        Complexity: O(log S) per get for S sets at that index.
        """
        h = self.hist[index]
        i = bisect.bisect_right(h, [snap_id, float("inf")]) - 1
        return h[i][1]


# Your SnapshotArray object will be instantiated and called as such:
# obj = SnapshotArray(length)
# obj.set(index,val)
# param_2 = obj.snap()
# param_3 = obj.get(index,snap_id)
# @lc code=end
