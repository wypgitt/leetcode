/**
 * Algorithm:
 * Emails are lowercased and masked as first + five stars + last + domain.
 * Phone numbers are normalized to digits, keep the last four local digits, and
 * mask the optional country code according to its length.
 *
 * Complexity:
 * Time O(n), space O(n) for digit normalization.
 */
class Solution {
    public String maskPII(String s) {
        if (s.indexOf('@') >= 0) {
            String lower = s.toLowerCase();
            int at = lower.indexOf('@');
            String name = lower.substring(0, at);
            String domain = lower.substring(at + 1);
            return name.charAt(0) + "*****" + name.charAt(name.length() - 1) + "@" + domain;
        }

        StringBuilder digits = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (Character.isDigit(ch)) {
                digits.append(ch);
            }
        }
        String local = "***-***-" + digits.substring(digits.length() - 4);
        int countryLen = digits.length() - 10;
        if (countryLen == 0) {
            return local;
        }
        StringBuilder ans = new StringBuilder("+");
        for (int i = 0; i < countryLen; i++) {
            ans.append('*');
        }
        ans.append('-').append(local);
        return ans.toString();
    }
}

