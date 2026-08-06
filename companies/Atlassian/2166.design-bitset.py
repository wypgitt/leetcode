#
# @lc app=leetcode id=2166 lang=python3
#
# [2166] Design Bitset
#
# https://leetcode.com/problems/design-bitset/description/
#
# algorithms
# Medium (32.87%)
# Likes:    616
# Dislikes: 50
# Total Accepted:    29.2K
# Total Submissions: 88.9K
# Testcase Example:  "[\"Bitset\",\"fix\",\"fix\",\"flip\",\"all\",\"unfix\",\"flip\",\"one\",\"unfix\",\"count\",\"toString\"]\n[[5],[3],[1],[],[],[0],[],[],[0],[],[]]"
#
# A Bitset is a data structure that compactly stores bits.
#
# Implement the Bitset class:
#
#
# Bitset(int size) Initializes the Bitset with size bits, all of which are 0.
#
#
# void fix(int idx) Updates the value of the bit at the index idx to 1. If the
# value was already 1, no change occurs.
#
#
# void unfix(int idx) Updates the value of the bit at the index idx to 0. If the
# value was already 0, no change occurs.
#
#
# void flip() Flips the values of each bit in the Bitset. In other words, all
# bits with value 0 will now have value 1 and vice versa.
#
#
# boolean all() Checks if the value of each bit in the Bitset is 1. Returns true
# if it satisfies the condition, false otherwise.
#
#
# boolean one() Checks if there is at least one bit in the Bitset with value 1.
# Returns true if it satisfies the condition, false otherwise.
#
#
# int count() Returns the total number of bits in the Bitset which have value 1.
#
#
# String toString() Returns the current composition of the Bitset. Note that in
# the resultant string, the character at the i^th index should coincide with the
# value at the i^th bit of the Bitset.
#
#
#
# Example 1:
#
# Input
# ["Bitset", "fix", "fix", "flip", "all", "unfix", "flip", "one", "unfix",
# "count", "toString"]
# [[5], [3], [1], [], [], [0], [], [], [0], [], []]
# Output
# [null, null, null, null, false, null, null, true, null, 2, "01010"]
#
# Explanation
# Bitset bs = new Bitset(5); // bitset = "00000".
# bs.fix(3);     // the value at idx = 3 is updated to 1, so bitset = "00010".
# bs.fix(1);     // the value at idx = 1 is updated to 1, so bitset = "01010".
# bs.flip();     // the value of each bit is flipped, so bitset = "10101".
# bs.all();      // return False, as not all values of the bitset are 1.
# bs.unfix(0);   // the value at idx = 0 is updated to 0, so bitset = "00101".
# bs.flip();     // the value of each bit is flipped, so bitset = "11010".
# bs.one();      // return True, as there is at least 1 index with value 1.
# bs.unfix(0);   // the value at idx = 0 is updated to 0, so bitset = "01010".
# bs.count();    // return 2, as there are 2 bits with value 1.
# bs.toString(); // return "01010", which is the composition of bitset.
#
#
#
# Constraints:
#
#
# 1 <= size <= 10^5
#
#
# 0 <= idx <= size - 1
#
#
# At most 10^5 calls will be made in total to fix, unfix, flip, all, one, count,
# and toString.
#
#
# At least one call will be made to all, one, count, or toString.
#
#
# At most 5 calls will be made to toString.
#

# @lc code=start
class Bitset:

    def __init__(self, size: int):
        """
        Interview explanation:
        Design a bitset of fixed size with fix/unfix/flip/all/one/count/toString.
        Flip must be O(1): keep a flipped flag and invert meaning of stored bits.

        Algorithm:
        - Store list of '0'/'1' chars (or bytes); flip_flag XOR; ones count of
          logical ones; update count on fix/unfix considering flip.

        Complexity: O(size) init.
        """
        self.n = size
        self.bits = ["0"] * size
        self.flipped = False
        self.ones = 0

    def fix(self, idx: int) -> None:
        """
        Interview explanation:
        Set bit idx to 1 (logical).

        Algorithm:
        - If current logical value is 0, flip stored bit and update ones.

        Complexity: O(1).
        """
        if self.flipped:
            # logical 1 means stored '0'
            if self.bits[idx] != "0":
                self.bits[idx] = "0"
                self.ones += 1
        else:
            if self.bits[idx] != "1":
                self.bits[idx] = "1"
                self.ones += 1

    def unfix(self, idx: int) -> None:
        """
        Interview explanation:
        Set bit idx to 0 (logical).

        Algorithm:
        - If current logical value is 1, flip stored bit and update ones.

        Complexity: O(1).
        """
        if self.flipped:
            if self.bits[idx] != "1":
                self.bits[idx] = "1"
                self.ones -= 1
        else:
            if self.bits[idx] != "0":
                self.bits[idx] = "0"
                self.ones -= 1

    def flip(self) -> None:
        """
        Interview explanation:
        Invert all bits in O(1) via flag; ones becomes n - ones.

        Algorithm:
        - flipped ^= True; ones = n - ones.

        Complexity: O(1).
        """
        self.flipped = not self.flipped
        self.ones = self.n - self.ones

    def all(self) -> bool:
        """
        Interview explanation:
        True iff every bit is 1.

        Algorithm:
        - ones == n.

        Complexity: O(1).
        """
        return self.ones == self.n

    def one(self) -> bool:
        """
        Interview explanation:
        True iff at least one bit is 1.

        Algorithm:
        - ones > 0.

        Complexity: O(1).
        """
        return self.ones > 0

    def count(self) -> int:
        """
        Interview explanation:
        Number of bits set to 1.

        Algorithm:
        - Return ones.

        Complexity: O(1).
        """
        return self.ones

    def toString(self) -> str:
        """
        Interview explanation:
        Return bit string of length size.

        Algorithm:
        - If flipped, invert each stored char when joining.

        Complexity: O(n).
        """
        if not self.flipped:
            return "".join(self.bits)
        return "".join("1" if c == "0" else "0" for c in self.bits)


# Your Bitset object will be instantiated and called as such:
# obj = Bitset(size)
# obj.fix(idx)
# obj.unfix(idx)
# obj.flip()
# param_4 = obj.all()
# param_5 = obj.one()
# param_6 = obj.count()
# param_7 = obj.toString()
# @lc code=end
