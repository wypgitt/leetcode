import java.util.ArrayList;
import java.util.List;

/*
 * 1023. Camelcase Matching
 */
class Solution {
    public List<Boolean> camelMatch(String[] queries, String pattern) {
        List<Boolean> answer = new ArrayList<>();
        for (String query : queries) {
            answer.add(matches(query, pattern));
        }
        return answer;
    }

    private boolean matches(String query, String pattern) {
        int patternIndex = 0;

        for (int i = 0; i < query.length(); i++) {
            char current = query.charAt(i);
            if (patternIndex < pattern.length() && current == pattern.charAt(patternIndex)) {
                patternIndex++;
            } else if (Character.isUpperCase(current)) {
                return false;
            }
        }

        return patternIndex == pattern.length();
    }
}

/*
Interview Explanation

Core idea:
A query matches if it can be created by inserting lowercase letters into the
pattern. Extra lowercase characters are harmless, but an extra uppercase
character can never be inserted and must fail.

Java data structures:
- ArrayList<Boolean> stores the result in the same order as queries.
- A single int pointer tracks how much of pattern has been matched.

Algorithm:
For each query:
1. Scan characters from left to right.
2. If the character equals pattern[patternIndex], consume it.
3. Otherwise, reject if it is uppercase.
4. Otherwise, ignore it as an inserted lowercase character.
5. Accept only if the whole pattern was consumed.

Correctness:
The scan accepts pattern characters in order and ignores only lowercase
insertions, exactly matching the allowed operation. Any unmatched uppercase
letter cannot be created by insertion, so rejecting is necessary. If all
pattern characters are consumed by the end, the query can be formed from the
pattern plus lowercase insertions.

Complexity:
Let T be the total length of all query strings. Time is O(T), and extra working
space is O(1), excluding the answer list.

Edge cases:
- Query equals pattern exactly: true.
- Query has extra lowercase letters: still true if pattern order is preserved.
- Query has extra uppercase letters: false.
- Pattern letters missing from query: false.
*/
