import java.util.*;

/**
 * Algorithm:
 * Convert the IP to a 32-bit number. At each step, choose the largest CIDR
 * block aligned at the current start that does not exceed the remaining count,
 * append it, and advance.
 *
 * Java data structures:
 * long is used for unsigned IPv4 arithmetic because Java int is signed.
 *
 * Complexity:
 * O(log n) blocks in practice, O(1) work per block; output space is O(blocks).
 */
class Solution {
    public List<String> ipToCIDR(String ip, int n) {
        long start = ipToLong(ip);
        List<String> ans = new ArrayList<>();
        while (n > 0) {
            long lowbit = start & -start;
            if (lowbit == 0) {
                lowbit = 1L << 32;
            }
            long block = lowbit;
            while (block > n) {
                block >>= 1;
            }
            int prefix = 32 - (Long.numberOfTrailingZeros(block));
            ans.add(longToIp(start) + "/" + prefix);
            start += block;
            n -= (int) block;
        }
        return ans;
    }

    private long ipToLong(String s) {
        long value = 0;
        for (String part : s.split("\\.")) {
            value = value * 256 + Integer.parseInt(part);
        }
        return value;
    }

    private String longToIp(long x) {
        return ((x >> 24) & 255) + "." +
               ((x >> 16) & 255) + "." +
               ((x >> 8) & 255) + "." +
               (x & 255);
    }
}

