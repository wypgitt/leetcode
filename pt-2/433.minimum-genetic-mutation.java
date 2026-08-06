import java.util.*;

/**
 * Algorithm:
 * Treat valid genes as nodes in an unweighted graph and one-character
 * mutations as edges. BFS returns the first, therefore shortest, path to the
 * target gene.
 *
 * Java data structures:
 * HashSet gives O(1) average validation and visited checks. ArrayDeque is the
 * queue for BFS.
 *
 * Complexity:
 * With B bank genes and fixed length L=8, time O(B * L * 4), space O(B).
 */
class Solution {
    public int minMutation(String startGene, String endGene, String[] bank) {
        Set<String> bankSet = new HashSet<>(Arrays.asList(bank));
        if (!bankSet.contains(endGene)) {
            return -1;
        }

        char[] choices = {'A', 'C', 'G', 'T'};
        Queue<String> q = new ArrayDeque<>();
        Set<String> seen = new HashSet<>();
        q.offer(startGene);
        seen.add(startGene);
        int steps = 0;

        while (!q.isEmpty()) {
            for (int size = q.size(); size > 0; size--) {
                String gene = q.poll();
                if (gene.equals(endGene)) {
                    return steps;
                }
                char[] chars = gene.toCharArray();
                for (int i = 0; i < chars.length; i++) {
                    char old = chars[i];
                    for (char ch : choices) {
                        if (ch == old) {
                            continue;
                        }
                        chars[i] = ch;
                        String next = new String(chars);
                        if (bankSet.contains(next) && seen.add(next)) {
                            q.offer(next);
                        }
                    }
                    chars[i] = old;
                }
            }
            steps++;
        }
        return -1;
    }
}

