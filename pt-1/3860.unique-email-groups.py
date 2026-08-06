#
# @lc app=leetcode id=3860 lang=python3
#
# [3860] Unique Email Groups
#
# https://leetcode.com/problems/unique-email-groups/description/
#
# algorithms
# Medium (86.74%)
# Likes:    6
# Dislikes: 2
# Total Accepted:    574
# Total Submissions: 662
# Testcase Example:  '["test.email+alex@leetcode.com", "test.e.mail+bob.cathy@leetcode.com", "testemail+david@lee.tcode.com"]'
#
# You are given an array of strings emails, where each string is a valid email
# address.
# 
# Two email addresses belong to the same group if both their normalized local
# names and normalized domain names are identical.
# 
# The normalization rules are as follows:
# 
# 
# The local name is the part before the '@' symbol.
# 
# 
# Ignore all dots '.'.
# Ignore everything after the first '+', if present.
# Convert to lowercase.
# 
# 
# The domain name is the part after the '@' symbol.
# 
# Convert to lowercase.
# 
# 
# 
# 
# Return an integer denoting the number of unique email groups after
# normalization.
# 
# 
# Example 1:
# 
# 
# Input: emails = ["test.email+alex@leetcode.com",
# "test.e.mail+bob.cathy@leetcode.com", "testemail+david@lee.tcode.com"]
# 
# Output: 2
# 
# Explanation:
# 
# 
# 
# 
# 
# Email
# Local
# Normalized Local
# Domain
# Normalized Domain
# Final Email
# 
# 
# 
# 
# test.email+alex@leetcode.com
# test.email+alex
# testemail
# leetcode.com
# leetcode.com
# testemail@leetcode.com
# 
# 
# test.e.mail+bob.cathy@leetcode.com
# test.e.mail+bob.cathy
# testemail
# leetcode.com
# leetcode.com
# testemail@leetcode.com
# 
# 
# testemail+david@lee.tcode.com
# testemail+david
# testemail
# lee.tcode.com
# lee.tcode.com
# testemail@lee.tcode.com
# 
# 
# 
# 
# Unique emails are ["testemail@leetcode.com", "testemail@lee.tcode.com"].
# Thus, the answer is 2.
# 
# Example 2:
# 
# 
# Input: emails = ["A@B.com", "a@b.com", "ab+xy@b.com", "a.b@b.com"]
# 
# Output: 2
# 
# Explanation:
# 
# 
# 
# 
# Email
# Local
# Normalized Local
# Domain
# Normalized Domain
# Final Email
# 
# 
# 
# 
# A@B.com
# A
# a
# B.com
# b.com
# a@b.com
# 
# 
# a@b.com
# a
# a
# b.com
# b.com
# a@b.com
# 
# 
# ab+xy@b.com
# ab+xy
# ab
# b.com
# b.com
# ab@b.com
# 
# 
# a.b@b.com
# a.b
# ab
# b.com
# b.com
# ab@b.com
# 
# 
# 
# 
# Unique emails are ["a@b.com", "ab@b.com"]. Thus, the answer is 2.
# 
# 
# Example 3:
# 
# 
# Input: emails = ["a.b+c.d+e@DoMain.com", "ab+xyz@domain.com",
# "ab@domain.com"]
# 
# Output: 1
# 
# Explanation:
# 
# 
# 
# 
# Email
# Local
# Normalized Local
# Domain
# Normalized Domain
# Final Email
# 
# 
# 
# 
# a.b+c.d+e@DoMain.com
# a.b+c.d+e
# ab
# DoMain.com
# domain.com
# ab@domain.com
# 
# 
# ab+xyz@domain.com
# ab+xyz
# ab
# domain.com
# domain.com
# ab@domain.com
# 
# 
# ab@domain.com
# ab
# ab
# domain.com
# domain.com
# ab@domain.com
# 
# 
# 
# 
# All emails normalize to "ab@domain.com". Thus, the answer is 1.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= emails.length <= 1000
# 1 <= emails[i].length <= 100
# emails[i] consists of lowercase and uppercase English letters, digits, and
# the characters '.', '+', and '@'.
# Each emails[i] contains exactly one '@' character.
# All local and domain names are non-empty; local names do not start with
# '+'.
# Domain names end with the ".com" suffix and contain at least one character
# before ".com".
# 
# 
#

# @lc code=start
class Solution:
    def uniqueEmailGroups(self, emails: list[str]) -> int:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We are given a list of valid email addresses.  Two emails belong to the
        same group if their normalized local names and normalized domain names
        are identical.

        Email structure:

            local@domain

        Local-name normalization:

        * ignore everything after the first '+'
        * remove all dots '.'
        * convert to lowercase

        Domain-name normalization:

        * convert to lowercase

        We need return the number of distinct normalized emails.

        Key observation
        ---------------
        The problem defines a canonical form for every email address.

        If two emails normalize to the same canonical string, they are in the
        same group.  If they normalize to different canonical strings, they are
        in different groups.

        So the task becomes:

            normalize every email
            count unique normalized strings

        Data structure choice
        ---------------------
        We use a set:

            normalized_emails = set()

        A set is ideal because:

        * it automatically removes duplicates
        * insertion is O(1) average time
        * its final length is exactly the number of unique groups

        Algorithm
        ---------
        For each email:

        1. Split once at '@':

               local, domain = email.split("@")

        2. Normalize the local name:

               local = local.lower()
               local = local.split("+", 1)[0]
               local = local.replace(".", "")

           The order of lowercasing, plus-trimming, and dot-removal does not
           change the final result here.  Lowercasing first keeps the code
           straightforward.

        3. Normalize the domain:

               domain = domain.lower()

        4. Combine:

               canonical = local + "@" + domain

        5. Add the canonical email to the set.

        Return the size of the set.

        Correctness proof
        -----------------
        Lemma 1: For every input email, the algorithm computes the normalized
        local name required by the problem.
        It discards everything after the first '+', removes every '.', and
        converts letters to lowercase.  These are exactly the local-name
        normalization rules.

        Lemma 2: For every input email, the algorithm computes the normalized
        domain name required by the problem.
        It converts the domain to lowercase and does not otherwise modify it,
        exactly matching the domain-name normalization rule.

        Lemma 3: Two emails are placed in the same set entry if and only if they
        belong to the same group.
        By Lemma 1 and Lemma 2, the canonical string built by the algorithm is
        exactly the normalized local name, followed by '@', followed by the
        normalized domain name.  Two such strings are equal exactly when both
        normalized parts are equal, which is the definition of being in the same
        group.

        Theorem: The algorithm returns the number of unique email groups.
        By Lemma 3, each group corresponds to exactly one canonical string in
        the set, and each canonical string corresponds to exactly one group.
        Therefore the number of groups equals the size of the set returned by
        the algorithm.

        Complexity analysis
        -------------------
        Let:

            n = number of emails
            L = maximum length of an email

        Each email is scanned a constant number of times by `split`, `lower`,
        and `replace`, so normalization costs O(L) per email.

        Total time:  O(n * L)
        Total space: O(n * L)

        The space is for storing up to n normalized email strings.

        Edge cases
        ----------
        * Uppercase letters:
              "A@B.com" and "a@b.com" normalize to the same email.

        * Multiple plus signs:
              only the first '+' matters; everything after it is ignored.

        * Dots after a plus:
              they are ignored because the entire suffix after '+' is ignored.

        * Dots in the domain:
              domain dots are kept.  Only local-name dots are removed.

        * No plus sign:
              the entire local name is kept before dot removal.

        Test strategy
        -------------
        Useful tests:

        * Provided examples.
        * Emails differing only by local dots.
        * Emails differing only by uppercase/lowercase.
        * Emails with multiple '+' signs in local name.
        * Same local normalization but different domains.

        Possible improvement?
        ---------------------
        This is already optimal for the constraints.  We must read every
        character that can affect normalization, so O(n * L) time is unavoidable.
        """

        normalized_emails: set[str] = set()

        for email in emails:
            local, domain = email.split("@")

            local = local.lower().split("+", 1)[0].replace(".", "")
            domain = domain.lower()

            normalized_emails.add(local + "@" + domain)

        return len(normalized_emails)
# @lc code=end
