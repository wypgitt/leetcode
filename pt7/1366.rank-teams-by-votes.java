import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/*
 * LeetCode 1366 - Rank Teams by Votes
 */
class Solution {
    public String rankTeams(String[] votes) {
        int positions = votes[0].length();
        int[][] counts = new int[26][positions];

        for (String vote : votes) {
            for (int position = 0; position < vote.length(); position++) {
                counts[vote.charAt(position) - 'A'][position]++;
            }
        }

        List<Character> teams = new ArrayList<>();
        for (char team : votes[0].toCharArray()) {
            teams.add(team);
        }

        Collections.sort(teams, (a, b) -> {
            for (int position = 0; position < positions; position++) {
                int countA = counts[a - 'A'][position];
                int countB = counts[b - 'A'][position];
                if (countA != countB) {
                    return Integer.compare(countB, countA);
                }
            }
            return Character.compare(a, b);
        });

        StringBuilder answer = new StringBuilder();
        for (char team : teams) {
            answer.append(team);
        }
        return answer.toString();
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Count how many votes each team receives at each rank. Sort teams by first
 * place count descending, then second place count descending, and so on. If all
 * counts tie, sort alphabetically.
 *
 * Java data structures:
 * `int[26][positions]` stores rank counts. A `List<Character>` is sorted with a
 * comparator that reads that table.
 *
 * Edge cases:
 * - One vote returns that vote.
 * - Complete tie falls back to alphabetical order.
 * - Team count is at most 26, so comparator work is tiny.
 *
 * Complexity:
 * Time O(v * t + t log t * t), with t <= 26.
 * Space O(26 * t).
 */
