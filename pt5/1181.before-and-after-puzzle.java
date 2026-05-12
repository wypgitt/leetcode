import java.util.*;

class Solution {
    public List<String> beforeAndAfterPuzzles(String[] phrases) {
        String[][] words = new String[phrases.length][];
        for (int i = 0; i < phrases.length; i++) {
            words[i] = phrases[i].split(" ");
        }

        Set<String> puzzles = new HashSet<>();
        for (int i = 0; i < phrases.length; i++) {
            for (int j = 0; j < phrases.length; j++) {
                if (i == j) {
                    continue;
                }
                String[] first = words[i];
                String[] second = words[j];
                if (!first[first.length - 1].equals(second[0])) {
                    continue;
                }

                StringBuilder merged = new StringBuilder(phrases[i]);
                for (int k = 1; k < second.length; k++) {
                    merged.append(' ').append(second[k]);
                }
                puzzles.add(merged.toString());
            }
        }

        List<String> answer = new ArrayList<>(puzzles);
        Collections.sort(answer);
        return answer;
    }
}

