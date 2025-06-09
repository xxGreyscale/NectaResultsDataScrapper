import re
import warnings

from fuzzywuzzy import process


def get_matching_name(df, target, threshold):
    results = process.extractOne(target.name.lower(), df["School Name"].str.lower(), score_cutoff=threshold)
    if results is None:
        new_target = re.sub(r"\b(?:school|seminary)\b", "", target.name, flags=re.IGNORECASE).strip()
        new_results = process.extractOne(new_target, df["School Name"].str.lower(), score_cutoff=threshold - 40)
        results = new_results if new_results else (None, None, None)
    best_match, score, index = results if results else (None, None, None)
    # Return the row
    if index is not None:
        row = df.iloc[index]
        # Check if the score is above the threshold
        return [row, score]  # the score here is returned as confidence level


def flexible_search_patterns(name):
    """
    :param name: The name of the school
    :return: A regex pattern that matches the name of the school
    Creates a regex pattern to match a school name, handling optional apostrophes at the end of the word
    and "seminary"/"seminari" variations, and only applies the seminary variation
    if "seminary" is present in the original name.
    """
    warnings.warn(
        "This function is not used anywhere in the code, and may not be used anymore in the future.",
        DeprecationWarning,
        stacklevel=2
    )
    name = name.lower()
    # Split the name into words
    words = name.split()
    # Create a regex pattern for each word
    patterns = []
    for word in words:
        # Handle optional apostrophes at the end of the word
        if word.endswith("'"):
            word = word[:-1]
        # Handle "seminary" and "seminari" variations
        if "seminary" in word:
            patterns.append(f"{word}|'?{word[:-2]}ri")
        else:
            patterns.append(word)
    # Join the patterns with optional spaces in between
    return r"\s*".join(patterns)
