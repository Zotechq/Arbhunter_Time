import re

abbrev_map = {
    'utd': 'united',
    'man': 'manchester',
    'cfc': 'chelsea',
    'lfc': 'liverpool',
    'ars': 'arsenal',
    'mci': 'manchester city',
    'tot': 'tottenham',
    'rm': 'real madrid',
    'bar': 'barcelona',
    'atm': 'atletico madrid',
    'fcb': 'bayern munich',
    'psg': 'paris saint germain',
    'juv': 'juventus',
    'int': 'inter milan',
    'mil': 'ac milan',
    'nap': 'napoli',
    'epl': 'premier league',
    'laliga': 'la liga',
    'ucl': 'champions league'
}

stop_words = {"fc", "united", "sc", "club", "real", "st", "bc"}

def normalize_name(name):
    name = name.lower()
    name = re.sub(r'[^a-z0-9\s]', '', name)  # Remove punctuation
    tokens = name.split()
    tokens = [abbrev_map.get(t, t) for t in tokens]
    filtered_tokens = [t for t in tokens if t not in stop_words]
    return ' '.join(filtered_tokens)

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def fuzzy_match(str1, str2, threshold=0.8):
    s1 = normalize_name(str1)
    s2 = normalize_name(str2)
    dist = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    similarity = 1 - (dist / max_len) if max_len else 1
    return similarity >= threshold