/*
 * @lc app=leetcode id=3845 lang=java
 *
 * [3845] Maximum Subarray XOR With Bounded Range
 *
 * Sliding window maintains max(nums[l..r]) - min(nums[l..r]) <= k with two
 * monotonic deques. Prefix XORs that can start valid subarrays are stored in a
 * binary trie; querying the current prefix gives the best XOR ending at r.
 *
 * Java note: the trie stores child indices in arrays and counts per node so
 * prefixes can be removed as the window left boundary advances.
 *
 * Time: O(n * B). Space: O(n * B), B = 15.
 */

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;

// @lc code=start
class Solution {
    public int maxXor(int[] nums, int k) {
        BinaryTrie trie = new BinaryTrie();
        ArrayDeque<Integer> maxQ = new ArrayDeque<>();
        ArrayDeque<Integer> minQ = new ArrayDeque<>();
        List<Integer> prefixes = new ArrayList<>();
        prefixes.add(0);

        int left = 0;
        int currentPrefix = 0;
        int answer = 0;

        for (int right = 0; right < nums.length; right++) {
            int value = nums[right];
            trie.insert(prefixes.get(right));

            while (!maxQ.isEmpty() && nums[maxQ.peekLast()] <= value) {
                maxQ.pollLast();
            }
            maxQ.addLast(right);

            while (!minQ.isEmpty() && nums[minQ.peekLast()] >= value) {
                minQ.pollLast();
            }
            minQ.addLast(right);

            while (nums[maxQ.peekFirst()] - nums[minQ.peekFirst()] > k) {
                trie.remove(prefixes.get(left));
                if (maxQ.peekFirst() == left) {
                    maxQ.pollFirst();
                }
                if (minQ.peekFirst() == left) {
                    minQ.pollFirst();
                }
                left++;
            }

            currentPrefix ^= value;
            answer = Math.max(answer, trie.maxXor(currentPrefix));
            prefixes.add(currentPrefix);
        }
        return answer;
    }

    private static class BinaryTrie {
        private static final int MAX_BIT = 14;
        private final List<int[]> child = new ArrayList<>();
        private final List<Integer> count = new ArrayList<>();

        BinaryTrie() {
            child.add(new int[] {-1, -1});
            count.add(0);
        }

        void insert(int value) {
            int node = 0;
            count.set(node, count.get(node) + 1);
            for (int bitIndex = MAX_BIT; bitIndex >= 0; bitIndex--) {
                int bit = (value >> bitIndex) & 1;
                int next = child.get(node)[bit];
                if (next == -1) {
                    next = child.size();
                    child.get(node)[bit] = next;
                    child.add(new int[] {-1, -1});
                    count.add(0);
                }
                node = next;
                count.set(node, count.get(node) + 1);
            }
        }

        void remove(int value) {
            int node = 0;
            count.set(node, count.get(node) - 1);
            for (int bitIndex = MAX_BIT; bitIndex >= 0; bitIndex--) {
                int bit = (value >> bitIndex) & 1;
                node = child.get(node)[bit];
                count.set(node, count.get(node) - 1);
            }
        }

        int maxXor(int value) {
            int node = 0;
            int best = 0;
            for (int bitIndex = MAX_BIT; bitIndex >= 0; bitIndex--) {
                int bit = (value >> bitIndex) & 1;
                int preferred = bit ^ 1;
                int preferredNode = child.get(node)[preferred];
                if (preferredNode != -1 && count.get(preferredNode) > 0) {
                    best |= 1 << bitIndex;
                    node = preferredNode;
                } else {
                    node = child.get(node)[bit];
                }
            }
            return best;
        }
    }
}
// @lc code=end
