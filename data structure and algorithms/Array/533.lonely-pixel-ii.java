/*
 * @lc app=leetcode id=533 lang=java
 *
 * [533] Lonely Pixel II
 *
 * Count each row pattern and each column's black pixels. A valid row pattern
 * must occur exactly target times and contain target black pixels; each 'B'
 * column with target black pixels contributes target valid pixels.
 *
 * Time: O(RC). Space: O(RC) for row-pattern strings.
 */

import java.util.HashMap;
import java.util.Map;

// @lc code=start
class Solution {
    public int findBlackPixel(char[][] picture, int target) {
        int rows = picture.length;
        int cols = picture[0].length;
        int[] columnBlack = new int[cols];
        Map<String, Integer> rowCount = new HashMap<>();

        for (char[] row : picture) {
            String pattern = new String(row);
            rowCount.merge(pattern, 1, Integer::sum);
            for (int c = 0; c < cols; c++) {
                if (row[c] == 'B') {
                    columnBlack[c]++;
                }
            }
        }

        int answer = 0;
        for (Map.Entry<String, Integer> entry : rowCount.entrySet()) {
            String pattern = entry.getKey();
            int occurrences = entry.getValue();
            if (occurrences != target || countBlack(pattern) != target) {
                continue;
            }
            for (int c = 0; c < cols; c++) {
                if (pattern.charAt(c) == 'B' && columnBlack[c] == target) {
                    answer += target;
                }
            }
        }
        return answer;
    }

    private int countBlack(String pattern) {
        int count = 0;
        for (int i = 0; i < pattern.length(); i++) {
            if (pattern.charAt(i) == 'B') {
                count++;
            }
        }
        return count;
    }
}
// @lc code=end
