/*
 * @lc app=leetcode id=1096 lang=java
 *
 * [1096] Brace Expansion II
 */

/*
 * --- Interview notes (grammar, innermost expansion, DFS, dedup, complexity, edges, tests) ---
 *
 * Grammar (informal)
 * • Literal lowercase letter x represents the singleton set {x}.
 * • Comma inside braces is union: R({e1,e2,...}) = R(e1) ∪ R(e2) ∪ … (each distinct word appears once in the
 *   final answer — duplicates from overlapping unions collapse).
 * • Juxtaposition is Cartesian concatenation: R(e1 e2) = { a+b | a ∈ R(e1), b ∈ R(e2) }.
 *
 * Algorithm — peel the innermost {...} first
 * Scan for the first closing brace `}` at index j (always pairs with some `{` to its left). Between that pair,
 * there are no nested braces yet — otherwise the first `}` would belong to an inner pair processed earlier.
 * Let i be the index of the matching `{` (take the last `{` strictly before j — i.e. the opener of this innermost
 * block). Split the substring exp[i+1:j] by commas into alternatives b₁, b₂, … that contain no `{`,`}`.
 * Recurse on each replacement: dfs(a + b_k + c) where a = exp[:i], c = exp[j+1:].
 * When no `}` remains, the string is fully expanded — add it to a set for uniqueness.
 * Finally return sorted(set).
 *
 * Why “first `}`, last `{` before it” finds an innermost block
 * The first closing brace closes whichever `{...}` started most recently still open — its matching `{` is the
 * nearest `{` leftward without crossing an outer `}` before j. Taking `rfind('{', 0, j)` is equivalent here because
 * nested deeper `{` appear closer to j than outer `{`.
 *
 * Why comma-split is safe at this step
 * By construction exp[i+1:j] cannot contain `{` or `}` — otherwise j would not be the first `}`.
 *
 * Data structures
 * • Python set[str]: automatically deduplicates union semantics for overlapping productions (Example 2).
 * • Result sorted lexicographically as required.
 *
 * Time complexity
 * Exponential in the number of alternatives in the worst case (Cartesian products grow multiplicatively). With
 * |expression| ≤ 60 the recursion depth and branching stay bounded for contest constraints; no tighter universal
 * polynomial bound is needed for interviews beyond “small input — DFS + caching via set”.
 *
 * Space complexity
 * O(K) for storing K distinct output strings plus recursion stack O(depth) ≤ O(n).
 *
 * Edge cases
 * • No braces: expression is a plain word — dfs reaches base case immediately.
 * • Nested braces: handled automatically by repeated innermost peeling.
 * • Duplicate words from different branches: set removes duplicates.
 *
 * Tests (statement)
 * "{a,b}{c,{d,e}}" → ["ac","ad","ae","bc","bd","be"]
 * "{{a,z},a{b,c},{ab,z}}" → ["a","ab","ac","z"]
 *
 * Improvements
 * • If inputs were huge, explicit trie / lazy merging might help — unnecessary here.
 *
 * --- end notes ---
 */

// @lc code=start
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class Solution {

    private Set<String> words;

    private void dfs(String exp) {
        int j = exp.indexOf('}');
        if (j == -1) {
            words.add(exp);
            return;
        }
        int i = exp.lastIndexOf('{', j - 1);
        String prefix = exp.substring(0, i);
        String suffix = exp.substring(j + 1);
        String middle = exp.substring(i + 1, j);
        for (String alt : middle.split(",")) {
            dfs(prefix + alt + suffix);
        }
    }

    public List<String> braceExpansionII(String expression) {
        words = new HashSet<>();
        dfs(expression);
        List<String> out = new ArrayList<>(words);
        Collections.sort(out);
        return out;
    }
}
// @lc code=end
