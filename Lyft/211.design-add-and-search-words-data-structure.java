/**
 * Algorithm:
 * Trie insertion is standard. Search supports '.' by recursively trying all
 * existing children at that position.
 *
 * Java data structures:
 * TrieNode[26] children array is efficient for lowercase English letters.
 *
 * Complexity:
 * addWord is O(length). search is O(length) without wildcards and worst-case
 * O(26^dots * length) with wildcards.
 */
class WordDictionary {
    private static class TrieNode {
        TrieNode[] children = new TrieNode[26];
        boolean word;
    }

    private final TrieNode root;

    public WordDictionary() {
        root = new TrieNode();
    }

    public void addWord(String word) {
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
        return dfs(0, root, word);
    }

    private boolean dfs(int i, TrieNode node, String word) {
        if (i == word.length()) {
            return node.word;
        }
        char ch = word.charAt(i);
        if (ch == '.') {
            for (TrieNode child : node.children) {
                if (child != null && dfs(i + 1, child, word)) {
                    return true;
                }
            }
            return false;
        }
        int idx = ch - 'a';
        return node.children[idx] != null && dfs(i + 1, node.children[idx], word);
    }
}

