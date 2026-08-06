/*
 * @lc app=leetcode id=411 lang=java
 *
 * [411] Minimum Unique Word Abbreviation
 *
 * A kept-character mask defines an abbreviation. For every dictionary word of
 * the same length, build a difference mask; an abbreviation is unique iff its
 * kept mask intersects every difference mask. Enumerate masks and keep the
 * shortest abbreviation.
 *
 * Java note: bit masks fit the LeetCode target length constraint and make
 * conflict checks O(dictionary size).
 *
 * Time: O(2^L * (D + L)). Space: O(D).
 */

import java.util.ArrayList;
import java.util.List;

// @lc code=start
class Solution {
    public String minAbbreviation(String target, String[] dictionary) {
        int length = target.length();
        List<Integer> differenceMasks = new ArrayList<>();

        for (String word : dictionary) {
            if (word.length() != length) {
                continue;
            }
            int diff = 0;
            for (int i = 0; i < length; i++) {
                if (target.charAt(i) != word.charAt(i)) {
                    diff |= 1 << i;
                }
            }
            differenceMasks.add(diff);
        }

        if (differenceMasks.isEmpty()) {
            return Integer.toString(length);
        }

        int bestMask = (1 << length) - 1;
        int bestLength = length;
        for (int mask = 0; mask < (1 << length); mask++) {
            int currentLength = abbreviationLength(mask, length);
            if (currentLength >= bestLength) {
                continue;
            }
            boolean unique = true;
            for (int diff : differenceMasks) {
                if ((mask & diff) == 0) {
                    unique = false;
                    break;
                }
            }
            if (unique) {
                bestMask = mask;
                bestLength = currentLength;
            }
        }
        return buildAbbreviation(target, bestMask);
    }

    private int abbreviationLength(int mask, int wordLength) {
        int length = 0;
        int index = 0;
        while (index < wordLength) {
            length++;
            if ((mask & (1 << index)) != 0) {
                index++;
            } else {
                while (index < wordLength && (mask & (1 << index)) == 0) {
                    index++;
                }
            }
        }
        return length;
    }

    private String buildAbbreviation(String target, int mask) {
        StringBuilder out = new StringBuilder();
        int abbreviated = 0;
        for (int i = 0; i < target.length(); i++) {
            if ((mask & (1 << i)) != 0) {
                if (abbreviated > 0) {
                    out.append(abbreviated);
                    abbreviated = 0;
                }
                out.append(target.charAt(i));
            } else {
                abbreviated++;
            }
        }
        if (abbreviated > 0) {
            out.append(abbreviated);
        }
        return out.toString();
    }
}
// @lc code=end
