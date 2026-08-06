/*
 * @lc app=leetcode id=3860 lang=java
 *
 * [3860] Unique Email Groups
 *
 * Normalize local names by lowercasing, removing dots, and ignoring everything
 * after '+'. Normalize domains by lowercasing. Count distinct normalized
 * addresses in a HashSet.
 *
 * Time: O(total characters). Space: O(number of emails).
 */

import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

// @lc code=start
class Solution {
    public int uniqueEmailGroups(String[] emails) {
        Set<String> normalized = new HashSet<>();
        for (String email : emails) {
            String[] parts = email.split("@", 2);
            String local = parts[0].toLowerCase(Locale.ROOT);
            int plus = local.indexOf('+');
            if (plus != -1) {
                local = local.substring(0, plus);
            }
            local = local.replace(".", "");
            String domain = parts[1].toLowerCase(Locale.ROOT);
            normalized.add(local + "@" + domain);
        }
        return normalized.size();
    }
}
// @lc code=end
