/**
 * Algorithm:
 * Compress the target and each word into character groups. A word group must
 * have the same character, no larger count than the target group, and if the
 * target group length is below 3 then the counts must match exactly.
 *
 * Java data structures:
 * Arrays of small Group objects keep the comparison explicit.
 *
 * Complexity:
 * Time O(|s| + total word length), space O(|s|) for target groups and O(word)
 * temporary groups.
 */
class Solution {
    public int expressiveWords(String s, String[] words) {
        Group[] target = groups(s);
        int ans = 0;
        for (String word : words) {
            Group[] current = groups(word);
            if (current.length != target.length) {
                continue;
            }
            boolean ok = true;
            for (int i = 0; i < target.length; i++) {
                int tn = target[i].count;
                int wn = current[i].count;
                if (target[i].ch != current[i].ch || wn > tn || (tn < 3 && wn != tn)) {
                    ok = false;
                    break;
                }
            }
            if (ok) {
                ans++;
            }
        }
        return ans;
    }

    private Group[] groups(String t) {
        java.util.List<Group> res = new java.util.ArrayList<>();
        int i = 0;
        while (i < t.length()) {
            int j = i + 1;
            while (j < t.length() && t.charAt(j) == t.charAt(i)) {
                j++;
            }
            res.add(new Group(t.charAt(i), j - i));
            i = j;
        }
        return res.toArray(new Group[0]);
    }

    private static class Group {
        char ch;
        int count;

        Group(char ch, int count) {
            this.ch = ch;
            this.count = count;
        }
    }
}

