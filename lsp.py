def split_equally_by_words(text, num_lines=2):
    # Split the text by spaces to get words
    words = text.split()
    
    # Calculate roughly the number of words per line
    words_per_line = max(1, len(words) // num_lines)
    
    # Create a list to hold the lines
    lines = []
    
    # Split the words into lines
    for i in range(num_lines - 1):
        # Take the next slice of words_per_line words
        line = ' '.join(words[i*words_per_line:(i+1)*words_per_line])
        lines.append(line)
    
    # Add the last line, which includes the remaining words
    lines.append(' '.join(words[(num_lines - 1)*words_per_line:]))
    
    # If the last line is significantly shorter, redistribute the words
    if lines[-1] and len(lines[-1].split()) < words_per_line / 2:
        # Redistribute the words more evenly
        return split_equally_by_words(text, num_lines - 1)
    
    return lines

# Original line to be split
line_to_split = ('count(*) INTO v_cnt_search_pkgs from stage_pkgs_outbound WHERE '
 "pkgs_search_processed = 'N' AND ready_to_process = 'Y' AND "
 "payment_rec_arrived = 'Y' AND dtc > p_cutoff_date")

# The variable num_lines controls the number of desired splits
num_lines = 3  # For example, change this to split into 3 lines

# Split the line into approximately equal-length lines
split_lines = split_equally_by_words(line_to_split, num_lines)

# Output the split lines
for index, line in enumerate(split_lines):
    print(f"Line {index + 1}: {line}")
