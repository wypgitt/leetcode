#
# @lc app=leetcode id=2286 lang=python3
#
# [2286] Booking Concert Tickets in Groups
#
# https://leetcode.com/problems/booking-concert-tickets-in-groups/description/
#
# algorithms
# Hard (19.97%)
# Likes:    356
# Dislikes: 62
# Total Accepted:    10.3K
# Total Submissions: 51.5K
# Testcase Example:  "[\"BookMyShow\",\"gather\",\"gather\",\"scatter\",\"scatter\"]\n[[2,5],[4,0],[2,0],[5,1],[5,1]]"
#
# A concert hall has n rows numbered from 0 to n - 1, each with m seats,
# numbered from 0 to m - 1. You need to design a ticketing system that can
# allocate seats in the following cases:
#
#
# If a group of k spectators can sit together in a row.
#
#
# If every member of a group of k spectators can get a seat. They may or may not
# sit together.
#
# Note that the spectators are very picky. Hence:
#
#
# They will book seats only if each member of their group can get a seat with
# row number less than or equal to maxRow. maxRow can vary from group to group.
#
#
# In case there are multiple rows to choose from, the row with the smallest
# number is chosen. If there are multiple seats to choose in the same row, the
# seat with the smallest number is chosen.
#
# Implement the BookMyShow class:
#
#
# BookMyShow(int n, int m) Initializes the object with n as number of rows and m
# as number of seats per row.
#
#
# int[] gather(int k, int maxRow) Returns an array of length 2 denoting the row
# and seat number (respectively) of the first seat being allocated to the k
# members of the group, who must sit together. In other words, it returns the
# smallest possible r and c such that all [c, c + k - 1] seats are valid and
# empty in row r, and r <= maxRow. Returns [] in case it is not possible to
# allocate seats to the group.
#
#
# boolean scatter(int k, int maxRow) Returns true if all k members of the group
# can be allocated seats in rows 0 to maxRow, who may or may not sit together.
# If the seats can be allocated, it allocates k seats to the group with the
# smallest row numbers, and the smallest possible seat numbers in each row.
# Otherwise, returns false.
#
#
#
# Example 1:
#
# Input
# ["BookMyShow", "gather", "gather", "scatter", "scatter"]
# [[2, 5], [4, 0], [2, 0], [5, 1], [5, 1]]
# Output
# [null, [0, 0], [], true, false]
#
# Explanation
# BookMyShow bms = new BookMyShow(2, 5); // There are 2 rows with 5 seats each
# bms.gather(4, 0); // return [0, 0]
#                   // The group books seats [0, 3] of row 0.
# bms.gather(2, 0); // return []
#                   // There is only 1 seat left in row 0,
#                   // so it is not possible to book 2 consecutive seats.
# bms.scatter(5, 1); // return True
#                    // The group books seat 4 of row 0 and seats [0, 3] of row
# 1.
# bms.scatter(5, 1); // return False
#                    // There is only one seat left in the hall.
#
#
#
# Constraints:
#
#
# 1 <= n <= 5 * 10^4
#
#
# 1 <= m, k <= 10^9
#
#
# 0 <= maxRow <= n - 1
#
#
# At most 5 * 10^4 calls in total will be made to gather and scatter.
#

# @lc code=start
from typing import List


class BookMyShow:
    def __init__(self, n: int, m: int):
        """
        Interview explanation:
        n rows x m seats; gather places k contiguous in one row <= maxRow;
        scatter fills any seats row-major <= maxRow.

        Algorithm:
        - Segment tree storing (max free in range, sum free); seats[i] free count.
        - gather: find leftmost row with free>=k; scatter: check sum then fill.

        Complexity: O(n) build; gather/scatter O(log n + rows touched).
        """
        self.n = n
        self.m = m
        self.seats = [m] * n
        size = 1
        while size < n:
            size <<= 1
        self.size = size
        self.mx = [0] * (2 * size)
        self.sm = [0] * (2 * size)
        for i in range(n):
            self.mx[size + i] = m
            self.sm[size + i] = m
        for i in range(size - 1, 0, -1):
            self.mx[i] = max(self.mx[2 * i], self.mx[2 * i + 1])
            self.sm[i] = self.sm[2 * i] + self.sm[2 * i + 1]

    def _update(self, row: int, free: int) -> None:
        i = self.size + row
        self.mx[i] = free
        self.sm[i] = free
        i //= 2
        while i:
            self.mx[i] = max(self.mx[2 * i], self.mx[2 * i + 1])
            self.sm[i] = self.sm[2 * i] + self.sm[2 * i + 1]
            i //= 2

    def _query_sum(self, r: int) -> int:
        """sum free in rows [0..r]"""
        l = self.size
        r = self.size + r
        res = 0
        while l <= r:
            if l & 1:
                res += self.sm[l]
                l += 1
            if not (r & 1):
                res += self.sm[r]
                r -= 1
            l //= 2
            r //= 2
        return res

    def _find_row(self, k: int, maxRow: int) -> int:
        """leftmost row <= maxRow with free >= k, or -1"""
        if self.mx[1] < k:
            return -1
        i = 1
        left, right = 0, self.size - 1
        while left != right:
            mid = (left + right) // 2
            if self.mx[2 * i] >= k:
                i = 2 * i
                right = mid
            else:
                i = 2 * i + 1
                left = mid + 1
        return left if left <= maxRow and self.seats[left] >= k else -1

    def gather(self, k: int, maxRow: int) -> List[int]:
        """
        Interview explanation:
        Book k contiguous seats in the lowest row <= maxRow that fits.

        Algorithm:
        - Segment-tree find leftmost row with free>=k; allocate from left of free.

        Complexity: O(log n).
        """
        row = self._find_row(k, maxRow)
        if row == -1:
            return []
        col = self.m - self.seats[row]
        self.seats[row] -= k
        self._update(row, self.seats[row])
        return [row, col]

    def scatter(self, k: int, maxRow: int) -> bool:
        """
        Interview explanation:
        Book k seats in row-major order among rows 0..maxRow if enough free.

        Algorithm:
        - If sum free >= k, fill from lowest rows sequentially.

        Complexity: O(rows touched + log n).
        """
        if self._query_sum(maxRow) < k:
            return False
        for row in range(maxRow + 1):
            if k == 0:
                break
            take = min(k, self.seats[row])
            if take:
                self.seats[row] -= take
                self._update(row, self.seats[row])
                k -= take
        return True


# Your BookMyShow object will be instantiated and called as such:
# obj = BookMyShow(n, m)
# param_1 = obj.gather(k,maxRow)
# param_2 = obj.scatter(k,maxRow)
# @lc code=end
