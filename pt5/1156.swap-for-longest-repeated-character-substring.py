from __future__ import annotations

from collections import Counter


class Solution:
    def maxRepOpt1(self, text: str) -> int:
        total = Counter(text)
        groups = []
        i = 0

        while i < len(text):
            j = i
            while j < len(text) and text[j] == text[i]:
                j += 1
            groups.append((text[i], j - i))
            i = j

        best = 0
        for char, length in groups:
            best = max(best, min(length + (total[char] > length), total[char]))

        for i in range(1, len(groups) - 1):
            middle_char, middle_length = groups[i]
            left_char, left_length = groups[i - 1]
            right_char, right_length = groups[i + 1]
            if middle_length == 1 and left_char == right_char:
                combined = left_length + right_length
                best = max(best, min(combined + (total[left_char] > combined), total[left_char]))

        return best

