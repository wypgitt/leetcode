#
# @lc app=leetcode id=1564 lang=python3
#
# [1564] Put Boxes Into the Warehouse I
#
# https://leetcode.com/problems/put-boxes-into-the-warehouse-i/description/
#
# algorithms
# Medium (67.91%)
# Likes:    344
# Dislikes: 30
# Total Accepted:    21K
# Total Submissions: 30.9K
# Testcase Example:  "[4,3,4,1]\n[5,3,3,4,1]"
#
#
# You are given two arrays of positive integers, boxes and warehouse,
# representing the heights of some boxes of unit width and the heights of
# n rooms in a warehouse respectively. The warehouse's rooms are labelled
# from 0 to n - 1 from left to right where warehouse[i] (0-indexed) is the
# height of the i^th room.
#
# Boxes are put into the warehouse by the following rules:
#
# Boxes cannot be stacked.
#
# You can rearrange the insertion order of the boxes.
#
# Boxes can only be pushed into the warehouse from left to right only.
#
# If the height of some room in the warehouse is less than the height of a
# box, then that box and all other boxes behind it will be stopped before
# that room.
#
# Return the maximum number of boxes you can put into the warehouse.
#
# Example 1:
#
# Input: boxes = [4,3,4,1], warehouse = [5,3,3,4,1]
# Output: 3
# Explanation:
#
# We can first put the box of height 1 in room 4. Then we can put the box
# of height 3 in either of the 3 rooms 1, 2, or 3. Lastly, we can put one
# box of height 4 in room 0.
# There is no way we can fit all 4 boxes in the warehouse.
#
# Example 2:
#
# Input: boxes = [1,2,2,3,4], warehouse = [3,4,1,2]
# Output: 3
# Explanation:
#
# Notice that it's not possible to put the box of height 4 into the
# warehouse since it cannot pass the first room of height 3.
# Also, for the last two rooms, 2 and 3, only boxes of height 1 can fit.
# We can fit 3 boxes maximum as shown above. The yellow box can also be
# put in room 2 instead.
# Swapping the orange and green boxes is also valid, or swapping one of
# them with the red box.
#
# Example 3:
#
# Input: boxes = [1,2,3], warehouse = [1,2,3,4]
# Output: 1
# Explanation: Since the first room in the warehouse is of height 1, we
# can only put boxes of height 1.
#
# Constraints:
#
# n == warehouse.length
#
# 1 <= boxes.length, warehouse.length <= 10^5
#
# 1 <= boxes[i], warehouse[i] <= 10^9
#
# @lc code=start
from typing import List


class Solution:
    def maxBoxesInWarehouse(self, boxes: List[int], warehouse: List[int]) -> int:
        """
        Interview explanation:
        Premium. Push boxes from left only; a box to room i must fit rooms
        0..i (cannot rearrange past taller). Effective height at i is
        min(warehouse[0..i]). Greedily assign smallest boxes to leftmost
        feasible rooms (or largest boxes from the back of effective heights).

        Algorithm:
        - effective[i]=min(warehouse[0..i]); sort boxes ascending.
        - Two pointers: try place smallest box into leftmost room that fits,
          or iterate rooms from left with boxes from small to large.
        - Classic: sort boxes desc; walk warehouse left→right placing if fits.

        Complexity: O(b log b + w) time, O(w) space.
        """
        w = warehouse[:]
        for i in range(1, len(w)):
            w[i] = min(w[i], w[i - 1])
        boxes = sorted(boxes)
        i = 0
        for h in reversed(w):
            if i < len(boxes) and boxes[i] <= h:
                i += 1
        return i

    def maxBoxesInWarehouse_desc(self, boxes: List[int], warehouse: List[int]) -> int:
        """
        Interview explanation:
        Alternate: sort boxes descending; place into warehouse from left when
        box fits current room (rooms already constrain via sequential push).

        Algorithm:
        - boxes.sort(reverse=True); i=0; for h in warehouse: while i<len and
          boxes[i]>h: i++; if i==len break; count++; i++.

        Complexity: O(b log b + w).
        """
        boxes = sorted(boxes, reverse=True)
        count = i = 0
        for h in warehouse:
            while i < len(boxes) and boxes[i] > h:
                i += 1
            if i == len(boxes):
                break
            count += 1
            i += 1
        return count
# @lc code=end

