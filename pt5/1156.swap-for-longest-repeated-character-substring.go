package main

type runGroup struct {
	char   byte
	length int
}

func maxRepOpt1(text string) int {
	total := [26]int{}
	for i := 0; i < len(text); i++ {
		total[text[i]-'a']++
	}

	groups := []runGroup{}
	for i := 0; i < len(text); {
		j := i
		for j < len(text) && text[j] == text[i] {
			j++
		}
		groups = append(groups, runGroup{char: text[i], length: j - i})
		i = j
	}

	best := 0
	for _, group := range groups {
		candidate := group.length
		if total[group.char-'a'] > group.length {
			candidate++
		}
		if candidate > total[group.char-'a'] {
			candidate = total[group.char-'a']
		}
		if candidate > best {
			best = candidate
		}
	}

	for i := 1; i+1 < len(groups); i++ {
		if groups[i].length == 1 && groups[i-1].char == groups[i+1].char {
			char := groups[i-1].char
			combined := groups[i-1].length + groups[i+1].length
			candidate := combined
			if total[char-'a'] > combined {
				candidate++
			}
			if candidate > total[char-'a'] {
				candidate = total[char-'a']
			}
			if candidate > best {
				best = candidate
			}
		}
	}

	return best
}

