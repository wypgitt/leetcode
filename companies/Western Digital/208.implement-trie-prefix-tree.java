/**
 * Algorithm:
 * Trie insertion walks/creates child nodes for each character and marks the
 * final node as a word. Search requires the final word marker; startsWith only
 * requires the prefix path to exist.
 *
 * Java data structures:
 * TrieNode has a fixed TrieNode[26] child array for lowercase English letters,
 * which is faster and simpler than a HashMap for this alphabet.
 *
 * Complexity:
 * insert/search/startsWith are O(length), space O(total inserted characters).
 */
class Trie {
    private static class TrieNode {
        TrieNode[] children = new TrieNode[26];
        boolean word;
    }

    private final TrieNode root;

    public Trie() {
        root = new TrieNode();
    }

    public void insert(String word) {
        TrieNode node = root;
        for (int i = 0; i < word.length(); i++) {
            int idx = word.charAt(i) - 'a';
            if (node.children[idx] == null) {
                node.children[idx] = new TrieNode();
            }
            node = node.children[idx];
        }
        node.word = true;
    }

    public boolean search(String word) {
        TrieNode node = find(word);
        return node != null && node.word;
    }

    public boolean startsWith(String prefix) {
        return find(prefix) != null;
    }

    private TrieNode find(String s) {
        TrieNode node = root;
        for (int i = 0; i < s.length(); i++) {
            int idx = s.charAt(i) - 'a';
            if (node.children[idx] == null) {
                return null;
            }
            node = node.children[idx];
        }
        return node;
    }
}

