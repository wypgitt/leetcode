import java.util.ArrayList;
import java.util.List;

/*
 * LeetCode 1324 - Print Words Vertically
 */
class Solution {
    public List<String> printVertically(String s) {
        String[] words = s.split(" ");
        int maxLength = 0;
        for (String word : words) {
            maxLength = Math.max(maxLength, word.length());
        }

        List<String> answer = new ArrayList<>();
        for (int col = 0; col < maxLength; col++) {
            StringBuilder builder = new StringBuilder();

            for (String word : words) {
                if (col < word.length()) {
                    builder.append(word.charAt(col));
                } else {
                    builder.append(' ');
                }
            }

            while (builder.length() > 0 && builder.charAt(builder.length() - 1) == ' ') {
                builder.deleteCharAt(builder.length() - 1);
            }

            answer.add(builder.toString());
        }

        return answer;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Reading the sentence vertically means reading the words column by column.
 * For column i, take the i-th character of every word that has one; otherwise
 * add a space to preserve alignment. Then trim only trailing spaces.
 *
 * Java data structures:
 * `String[]` stores the words. `StringBuilder` efficiently builds each output
 * row and lets us remove trailing spaces.
 *
 * Edge cases:
 * - One word returns one-character strings.
 * - Shorter words require internal spaces if later words still have letters.
 * - Trailing spaces must be removed, but leading/internal spaces must remain.
 *
 * Complexity:
 * Time O(w * L), where w is number of words and L is max word length.
 * Space O(w * L), mainly for the output.
 */
