import java.util.ArrayList;
import java.util.List;

class Solution {
    public List<Integer> sequentialDigits(int low, int high) {
        String digits = "123456789";
        List<Integer> ans = new ArrayList<>();

        for (int length = 2; length <= 9; length++) {
            for (int start = 0; start + length <= digits.length(); start++) {
                int num = Integer.parseInt(digits.substring(start, start + length));
                if (num >= low && num <= high) {
                    ans.add(num);
                }
            }
        }

        return ans;
    }
}

/*
Explanation

Every sequential-digit number is a contiguous substring of "123456789" with
length at least 2. Generate those substrings and keep the numbers inside
[low, high].

There are only 36 possible candidates, so direct generation is simpler and
faster than scanning the numeric range.

Edge cases: no valid number in range; low/high near one digit; 789 is valid but
890 is not because digits must be consecutive from 1 to 9.

Time complexity: O(1), fixed candidate count.
Space complexity: O(1) besides the answer.
*/
