import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class Solution {
    private final Map<String, String> parent = new HashMap<>();

    public List<String> generateSentences(List<List<String>> synonyms, String text) {
        for (List<String> pair : synonyms) {
            union(pair.get(0), pair.get(1));
        }

        Map<String, List<String>> groups = new HashMap<>();
        for (String word : new ArrayList<>(parent.keySet())) {
            groups.computeIfAbsent(find(word), key -> new ArrayList<>()).add(word);
        }

        Map<String, List<String>> choices = new HashMap<>();
        for (List<String> words : groups.values()) {
            Collections.sort(words);
            for (String word : words) {
                choices.put(word, words);
            }
        }

        String[] sentence = text.split(" ");
        List<String> ans = new ArrayList<>();
        backtrack(sentence, 0, choices, new ArrayList<>(), ans);
        return ans;
    }

    private void backtrack(
            String[] sentence,
            int index,
            Map<String, List<String>> choices,
            List<String> path,
            List<String> ans) {
        if (index == sentence.length) {
            ans.add(String.join(" ", path));
            return;
        }

        List<String> options = choices.getOrDefault(sentence[index], Collections.singletonList(sentence[index]));
        for (String option : options) {
            path.add(option);
            backtrack(sentence, index + 1, choices, path, ans);
            path.remove(path.size() - 1);
        }
    }

    private String find(String word) {
        parent.putIfAbsent(word, word);
        if (!parent.get(word).equals(word)) {
            parent.put(word, find(parent.get(word)));
        }
        return parent.get(word);
    }

    private void union(String a, String b) {
        String rootA = find(a);
        String rootB = find(b);
        if (!rootA.equals(rootB)) {
            parent.put(rootB, rootA);
        }
    }
}

/*
Explanation

Synonyms form connected components, so union-find groups all words that can
replace each other. Sort every component. Then backtrack through the sentence,
using the sorted synonym list for synonym words and the original word for
non-synonyms.

Union-find is the right Java data structure because synonym relationships are
transitive. Sorting each component makes the generated sentences lexicographic.

Edge cases: words with no synonyms; synonym chains; duplicate synonym pairs.

Time complexity: O(S alpha(W) + R * L), where R is the number of generated
sentences and L is sentence length.
Space complexity: O(W + R * L).
*/
