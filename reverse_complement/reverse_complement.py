def reverse(text):

    # input: a string of bases

    # returns: a string of bases in reverse order

    rev_text = ''

    for i in range(len(text) - 1, -1, -1):

        rev_text += text[i]

    return rev_text

def complementOf(base):
    # input: a single character string
    # returns: a single character string
    # the complementary base

    pair = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}

    # Check if the base is in the dictionary, return its complement, otherwise return the original base
    return pair.get(base.upper(), base)

def ReverseComplement(Pattern):
    # input: a string Pattern
    # returns: the reverse complement of Pattern

    # Use the custom reverse function to reverse the sequence
    reverse_complement = ''.join(complementOf(base) for base in reverse(Pattern))

    return reverse_complement

