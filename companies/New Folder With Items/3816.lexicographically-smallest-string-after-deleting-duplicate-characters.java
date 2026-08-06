/*
 * @lc app=leetcode id=3816 lang=java
 *
 * [3816] Lexicographically Smallest String After Deleting Duplicate Characters
 *
 * Build the answer greedily. At each step, try characters from 'a' to 'z' at
 * their next available position; choose the first one whose position still
 * leaves a later occurrence for every missing character.
 *
 * Java note: per-letter position lists plus pointer arrays avoid repeated scans
 * of the whole string.
 *
 * Time: O(26 * distinct letters + n). Space: O(n).
 */

import java.util.ArrayList;
import java.util.List;

// @lc code=start
class Solution {
    public String lexSmallestAfterDeletion(String s) {
        List<Integer>[] positions = new ArrayList[26];
        for (int i = 0; i < 26; i++) {
            positions[i] = new ArrayList<>();
        }
        for (int i = 0; i < s.length(); i++) {
            positions[s.charAt(i) - 'a'].add(i);
        }

        int[] last = new int[26];
        int missing = 0;
        for (int ch = 0; ch < 26; ch++) {
            last[ch] = -1;
            if (!positions[ch].isEmpty()) {
                last[ch] = positions[ch].get(positions[ch].size() - 1);
                missing |= 1 << ch;
            }
        }

        int[] ptr = new int[26];
        int start = 0;
        StringBuilder answer = new StringBuilder();

        while (missing != 0) {
            for (int ch = 0; ch < 26; ch++) {
                List<Integer> list = positions[ch];
                while (ptr[ch] < list.size() && list.get(ptr[ch]) < start) {
                    ptr[ch]++;
                }
                if (ptr[ch] == list.size()) {
                    continue;
                }
                int index = list.get(ptr[ch]);
                int newMissing = missing & ~(1 << ch);
                if (canFinishAfter(index, newMissing, last)) {
                    answer.append((char) ('a' + ch));
                    start = index + 1;
                    missing = newMissing;
                    break;
                }
            }
        }
        return answer.toString();
    }

    private boolean canFinishAfter(int index, int missing, int[] last) {
        for (int ch = 0; ch < 26; ch++) {
            if (((missing >> ch) & 1) == 1 && last[ch] <= index) {
                return false;
            }
        }
        return true;
    }
}
// @lc code=end
