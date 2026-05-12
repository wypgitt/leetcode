import java.util.*;

class Solution {
    public int maxRepOpt1(String text) {
        int[] total = new int[26];
        for (int i = 0; i < text.length(); i++) {
            total[text.charAt(i) - 'a']++;
        }

        List<Group> groups = new ArrayList<>();
        for (int i = 0; i < text.length(); ) {
            int j = i;
            while (j < text.length() && text.charAt(j) == text.charAt(i)) {
                j++;
            }
            groups.add(new Group(text.charAt(i), j - i));
            i = j;
        }

        int best = 0;
        for (Group group : groups) {
            int count = total[group.ch - 'a'];
            best = Math.max(best, Math.min(group.length + (count > group.length ? 1 : 0), count));
        }

        for (int i = 1; i + 1 < groups.size(); i++) {
            Group middle = groups.get(i);
            Group left = groups.get(i - 1);
            Group right = groups.get(i + 1);
            if (middle.length == 1 && left.ch == right.ch) {
                int combined = left.length + right.length;
                int count = total[left.ch - 'a'];
                best = Math.max(best, Math.min(combined + (count > combined ? 1 : 0), count));
            }
        }

        return best;
    }

    private static class Group {
        char ch;
        int length;

        Group(char ch, int length) {
            this.ch = ch;
            this.length = length;
        }
    }
}

