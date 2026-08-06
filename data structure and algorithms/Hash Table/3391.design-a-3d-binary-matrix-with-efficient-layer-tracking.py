#
# @lc app=leetcode id=3391 lang=python3
#
# [3391] Design a 3D Binary Matrix with Efficient Layer Tracking
#
# https://leetcode.com/problems/design-a-3d-binary-matrix-with-efficient-layer-tracking/description/
#
# algorithms
# Medium (66.42%)
# Likes:    9
# Dislikes: 1
# Total Accepted:    1.2K
# Total Submissions: 1.9K
# Testcase Example:  "[\"Matrix3D\",\"setCell\",\"largestMatrix\",\"setCell\",\"largestMatrix\",\"setCell\",\"largestMatrix\"]\n[[3],[0,0,0],[],[1,1,2],[],[0,0,1],[]]"
#
#
# You are given a n x n x n binary 3D array matrix.
#
# Implement the Matrix3D class:
#
# Matrix3D(int n) Initializes the object with the 3D binary array matrix,
# where all elements are initially set to 0.
#
# void setCell(int x, int y, int z) Sets the value at matrix[x][y][z] to
# 1.
#
# void unsetCell(int x, int y, int z) Sets the value at matrix[x][y][z] to
# 0.
#
# int largestMatrix() Returns the index x where matrix[x] contains the
# most number of 1's. If there are multiple such indices, return the
# largest x.
#
# Example 1:
#
# Input:
#
# ["Matrix3D", "setCell", "largestMatrix", "setCell", "largestMatrix",
# "setCell", "largestMatrix"]
#
# [[3], [0, 0, 0], [], [1, 1, 2], [], [0, 0, 1], []]
#
# Output:
#
# [null, null, 0, null, 1, null, 0]
#
# Explanation
#
# Matrix3D matrix3D = new Matrix3D(3); // Initializes a 3 x 3 x 3 3D array
# matrix, filled with all 0's.
#
# matrix3D.setCell(0, 0, 0); // Sets matrix[0][0][0] to 1.
#
# matrix3D.largestMatrix(); // Returns 0. matrix[0] has the most number of
# 1's.
#
# matrix3D.setCell(1, 1, 2); // Sets matrix[1][1][2] to 1.
#
# matrix3D.largestMatrix(); // Returns 1. matrix[0] and matrix[1] tie with
# the most number of 1's, but index 1 is bigger.
#
# matrix3D.setCell(0, 0, 1); // Sets matrix[0][0][1] to 1.
#
# matrix3D.largestMatrix(); // Returns 0. matrix[0] has the most number of
# 1's.
#
# Example 2:
#
# Input:
#
# ["Matrix3D", "setCell", "largestMatrix", "unsetCell", "largestMatrix"]
#
# [[4], [2, 1, 1], [], [2, 1, 1], []]
#
# Output:
#
# [null, null, 2, null, 3]
#
# Explanation
#
# Matrix3D matrix3D = new Matrix3D(4); // Initializes a 4 x 4 x 4 3D array
# matrix, filled with all 0's.
#
# matrix3D.setCell(2, 1, 1); // Sets matrix[2][1][1] to 1.
#
# matrix3D.largestMatrix(); // Returns 2. matrix[2] has the most number of
# 1's.
#
# matrix3D.unsetCell(2, 1, 1); // Sets matrix[2][1][1] to 0.
#
# matrix3D.largestMatrix(); // Returns 3. All indices from 0 to 3 tie with
# the same number of 1's, but index 3 is the biggest.
#
# Constraints:
#
# 1 <= n <= 100
#
# 0 <= x, y, z < n
#
# At most 10^5 calls are made in total to setCell and unsetCell.
#
# At most 10^4 calls are made to largestMatrix.
#

# @lc code=start

class Matrix3D:
    """
    Interview explanation:
    Track a binary n^3 cube; largestMatrix returns the layer x with the most 1s
    (largest x on ties). With n <= 100 and many updates, store set bits per layer
    and a count array — O(1) set/unset, O(n) largest scan (or heap if desired).

    Algorithm:
    - cells[x] = set of (y,z) that are 1; cnt[x] = |cells[x]|.
    - set/unset update set membership and cnt; largestMatrix argmax cnt then x.

    Complexity: O(1) set/unset, O(n) largestMatrix; O(n^2) worst space of 1s.
    """

    def __init__(self, n: int):
        self.n = n
        self.cells = [set() for _ in range(n)]
        self.cnt = [0] * n

    def setCell(self, x: int, y: int, z: int) -> None:
        """
        Interview explanation:
        Set matrix[x][y][z] to 1 (idempotent).

        Algorithm:
        - If (y,z) new in layer x, add it and increment cnt[x].

        Complexity: O(1) time.
        """
        key = (y, z)
        if key not in self.cells[x]:
            self.cells[x].add(key)
            self.cnt[x] += 1

    def unsetCell(self, x: int, y: int, z: int) -> None:
        """
        Interview explanation:
        Set matrix[x][y][z] to 0 (idempotent).

        Algorithm:
        - If (y,z) present in layer x, remove and decrement cnt[x].

        Complexity: O(1) time.
        """
        key = (y, z)
        if key in self.cells[x]:
            self.cells[x].remove(key)
            self.cnt[x] -= 1

    def largestMatrix(self) -> int:
        """
        Interview explanation:
        Return layer index with the most 1s; ties -> largest index.

        Algorithm:
        - Scan cnt; keep best where cnt[x] >= cnt[best].

        Complexity: O(n) time, O(1) space.
        """
        best = 0
        for x in range(1, self.n):
            if self.cnt[x] >= self.cnt[best]:
                best = x
        return best


# Your Matrix3D object will be instantiated and called as such:
# obj = Matrix3D(n)
# obj.setCell(x,y,z)
# obj.unsetCell(x,y,z)
# param_3 = obj.largestMatrix()
# @lc code=end
