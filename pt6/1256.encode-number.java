class Solution {
    public String encode(int num) {
        return Integer.toBinaryString(num + 1).substring(1);
    }
}

/*
Explanation

The code for num is the binary representation of num + 1 with the leading 1
removed. For example, 23 + 1 = 24, binary "11000", so the answer is "1000".

Java's Integer.toBinaryString gives the binary text directly.

Edge case: num == 0 produces "1", and removing the leading 1 gives the empty
string.

Time complexity: O(log num).
Space complexity: O(log num) for the returned string.
*/
