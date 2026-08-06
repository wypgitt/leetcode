#
# @lc app=leetcode id=1622 lang=python3
#
# [1622] Fancy Sequence
#
# https://leetcode.com/problems/fancy-sequence/description/
#
# algorithms
# Hard (41.55%)
# Likes:    645
# Dislikes: 184
# Total Accepted:    78.4K
# Total Submissions: 189K
# Testcase Example:  "[\"Fancy\",\"append\",\"addAll\",\"append\",\"multAll\",\"getIndex\",\"addAll\",\"append\",\"multAll\",\"getIndex\",\"getIndex\",\"getIndex\"]"
#
# Write an API that generates fancy sequences using the append, addAll, and
# multAll operations.
#
# Implement the Fancy class:
#
# Fancy() Initializes the object with an empty sequence.
#
# void append(val) Appends an integer val to the end of the sequence.
#
# void addAll(inc) Increments all existing values in the sequence by an integer
# inc.
#
# void multAll(m) Multiplies all existing values in the sequence by an integer
# m.
#
# int getIndex(idx) Gets the current value at index idx (0-indexed) of the
# sequence modulo 10^9 + 7. If the index is greater or equal than the length of
# the sequence, return -1.
#
# Example 1:
#
# Input
# ["Fancy", "append", "addAll", "append", "multAll", "getIndex", "addAll",
# "append", "multAll", "getIndex", "getIndex", "getIndex"]
# [[], [2], [3], [7], [2], [0], [3], [10], [2], [0], [1], [2]]
# Output
# [null, null, null, null, null, 10, null, null, null, 26, 34, 20]
#
# Explanation
# Fancy fancy = new Fancy();
# fancy.append(2); // fancy sequence: [2]
# fancy.addAll(3); // fancy sequence: [2+3] -> [5]
# fancy.append(7); // fancy sequence: [5, 7]
# fancy.multAll(2); // fancy sequence: [5*2, 7*2] -> [10, 14]
# fancy.getIndex(0); // return 10
# fancy.addAll(3); // fancy sequence: [10+3, 14+3] -> [13, 17]
# fancy.append(10); // fancy sequence: [13, 17, 10]
# fancy.multAll(2); // fancy sequence: [13*2, 17*2, 10*2] -> [26, 34, 20]
# fancy.getIndex(0); // return 26
# fancy.getIndex(1); // return 34
# fancy.getIndex(2); // return 20
#
# Constraints:
#
# 1 <= val, inc, m <= 100
#
# 0 <= idx <= 10^5
#
# At most 10^5 calls total will be made to append, addAll, multAll, and
# getIndex.
#

# @lc code=start
class Fancy:
    def __init__(self):
        """
        Interview explanation:
        Maintain sequence with append, addAll, multAll, getIndex under mod 1e9+7.
        Lazy affine transform: each appended value stored "normalized" under
        inverse of current global (mul, add) so get applies current transform.

        Algorithm:
        - vals list; global mul=1, add=0. append stores (val-add)*inv(mul).
        - addAll: add += inc. multAll: mul*=m; add*=m.
        - get: vals[i]*mul+add.

        Complexity: O(1) amortized per op with modinv.
        """
        self.MOD = 10**9 + 7
        self.vals = []
        self.mul = 1
        self.add = 0

    def append(self, val: int) -> None:
        """
        Interview explanation:
        Store value stripped of current lazy (mul,add) so later get reapplies them.

        Algorithm:
        - vals.append((val - add) * modinv(mul) % MOD)

        Complexity: O(1) with Fermat inv, or O(log MOD).
        """
        MOD = self.MOD
        x = (val - self.add) % MOD
        x = x * pow(self.mul, MOD - 2, MOD) % MOD
        self.vals.append(x)

    def addAll(self, inc: int) -> None:
        """
        Interview explanation:
        Lazy add to all current elements.

        Algorithm:
        - add = (add + inc) % MOD

        Complexity: O(1).
        """
        self.add = (self.add + inc) % self.MOD

    def multAll(self, m: int) -> None:
        """
        Interview explanation:
        Lazy multiply all current elements (and pending add).

        Algorithm:
        - mul = mul*m % MOD; add = add*m % MOD

        Complexity: O(1).
        """
        self.mul = self.mul * m % self.MOD
        self.add = self.add * m % self.MOD

    def getIndex(self, idx: int) -> int:
        """
        Interview explanation:
        Apply current affine transform to stored normalized value.

        Algorithm:
        - if idx >= len: -1 else (vals[idx]*mul + add) % MOD

        Complexity: O(1).
        """
        if idx >= len(self.vals):
            return -1
        return (self.vals[idx] * self.mul + self.add) % self.MOD


# Your Fancy object will be instantiated and called as such:
# obj = Fancy()
# obj.append(val)
# obj.addAll(inc)
# obj.multAll(m)
# param_4 = obj.getIndex(idx)
# @lc code=end
