/*
 * @lc app=leetcode id=3900 lang=java
 *
 * [3900] Longest Balanced Substring After One Swap
 *
 * Prefix balance (+1 for '1', -1 for '0') gives balanced substrings when two
 * prefix values match. One swap can fix substrings whose original balance is
 * +/-2 if there is an opposite character outside; cap lengths by available
 * outside characters and binary-search prefix positions.
 *
 * Java note: HashMap<Integer,List<Integer>> groups prefix positions by balance.
 *
 * Time: O(n log n). Space: O(n).
 */

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// @lc code=start
class Solution {
    public int longestBalanced(String s) {
        int totalZeros = 0;
        for (int i = 0; i < s.length(); i++) {
            if (s.charAt(i) == '0') {
                totalZeros++;
            }
        }
        int totalOnes = s.length() - totalZeros;

        int[] prefix = new int[s.length() + 1];
        Map<Integer, List<Integer>> positions = new HashMap<>();
        positions.computeIfAbsent(0, unused -> new ArrayList<>()).add(0);

        int balance = 0;
        for (int i = 1; i <= s.length(); i++) {
            balance += s.charAt(i - 1) == '1' ? 1 : -1;
            prefix[i] = balance;
            positions.computeIfAbsent(balance, unused -> new ArrayList<>()).add(i);
        }

        int answer = 0;
        Map<Integer, Integer> earliest = new HashMap<>();
        for (int i = 0; i < prefix.length; i++) {
            Integer first = earliest.get(prefix[i]);
            if (first == null) {
                earliest.put(prefix[i], i);
            } else {
                answer = Math.max(answer, i - first);
            }
        }

        int capTooManyOnes = 2 * totalZeros;
        int capTooManyZeros = 2 * totalOnes;
        for (int right = 1; right < prefix.length; right++) {
            int bal = prefix[right];
            answer = Math.max(answer, bestWithCap(positions.getOrDefault(bal - 2, List.of()), right, capTooManyOnes));
            answer = Math.max(answer, bestWithCap(positions.getOrDefault(bal + 2, List.of()), right, capTooManyZeros));
        }
        return answer;
    }

    private int bestWithCap(List<Integer> starts, int right, int cap) {
        if (cap <= 0) {
            return 0;
        }
        int index = lowerBound(starts, right - cap);
        if (index < starts.size() && starts.get(index) < right) {
            return right - starts.get(index);
        }
        return 0;
    }

    private int lowerBound(List<Integer> values, int target) {
        int lo = 0;
        int hi = values.size();
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (values.get(mid) < target) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        return lo;
    }
}
// @lc code=end
