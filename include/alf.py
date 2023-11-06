from pyparsing import Word, alphas, alphanums, Combine, Optional

# Define what constitutes a 'name' in our grammar: typically starting with a letter or underscore, 
# followed by any number of alphanumeric characters or underscores.
identifier = Combine(Optional(Word('_')) + Word(alphas + '_', alphanums + '_'))

# Example usage
parsed_result = identifier.parseString("v_location_name2")

print(parsed_result) 