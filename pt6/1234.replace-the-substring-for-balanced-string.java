class Solution {
    public int balancedString(String s) {
        int n = s.length();
        int limit = n / 4;
        int[] count = new int[128];

        for (char ch : s.toCharArray()) {
            count[ch]++;
        }

        if (isBalancedOutside(count, limit)) {
            return 0;
        }

        int ans = n;
        int left = 0;
        for (int right = 0; right < n; right++) {
            count[s.charAt(right)]--;

            while (left <= right && isBalancedOutside(count, limit)) {
                ans = Math.min(ans, right - left + 1);
                count[s.charAt(left)]++;
                left++;
            }
        }

        return ans;
    }

    private boolean isBalancedOutside(int[] count, int limit) {
        return count['Q'] <= limit
                && count['W'] <= limit
                && count['E'] <= limit
                && count['R'] <= limit;
    }
}

/*
Explanation

The replacement substring can be anything. Therefore, a window is valid if the
characters outside it already have at most n/4 of Q, W, E, and R. Count the
whole string, slide a window, and subtract characters inside the window from
the outside counts.

An int array indexed by char is faster and simpler than a HashMap because the
alphabet is tiny and fixed. The window shrinks whenever the outside counts are
valid to minimize the replacement length.

Edge cases: already balanced returns 0; one character over quota; repeated
shrinking finds the minimum.

Time complexity: O(n).
Space complexity: O(1).
*/
