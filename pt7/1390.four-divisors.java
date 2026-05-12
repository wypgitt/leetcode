/*
 * LeetCode 1390 - Four Divisors
 */
class Solution {
    public int sumFourDivisors(int[] nums) {
        int answer = 0;
        for (int num : nums) {
            answer += divisorSumIfFour(num);
        }
        return answer;
    }

    private int divisorSumIfFour(int num) {
        int count = 0;
        int sum = 0;

        for (int divisor = 1; divisor * divisor <= num; divisor++) {
            if (num % divisor != 0) {
                continue;
            }

            int other = num / divisor;
            if (divisor == other) {
                count++;
                sum += divisor;
            } else {
                count += 2;
                sum += divisor + other;
            }

            if (count > 4) {
                return 0;
            }
        }

        return count == 4 ? sum : 0;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * For each number, enumerate divisor pairs up to sqrt(num). Count distinct
 * divisors and sum them. Contribute the sum only if the count is exactly four.
 *
 * Java data structures:
 * Plain integer counters are enough: `count` for number of divisors and `sum`
 * for their total.
 *
 * Edge cases:
 * - Prime numbers have only two divisors and contribute 0.
 * - Perfect squares should not double-count the square root divisor.
 * - Stop early when count exceeds four.
 *
 * Complexity:
 * Time O(n * sqrt(M)), where M is the largest number.
 * Space O(1).
 */
