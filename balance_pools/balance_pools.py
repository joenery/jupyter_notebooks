def calculate_additional_DNA(sample1_reads, sample2_reads, sample1_amount, sample2_amount, sample1_conc, sample2_conc):
    """
    Calculate the additional amount of DNA needed to balance the number of reads between two samples.

    Args:
        sample1_reads (int): Number of reads for sample 1.
        sample2_reads (int): Number of reads for sample 2.
        sample1_amount (float): Amount of DNA added for sample 1 in ng.
        sample2_amount (float): Amount of DNA added for sample 2 in ng.
        sample1_conc (float): Concentration of DNA for sample 1 in ng/µl.
        sample2_conc (float): Concentration of DNA for sample 2 in ng/µl.

    Returns:
        tuple: A tuple containing the additional amount of DNA needed for each sample and the ratio of concentrations.
    """
    # Calculate ratios
    ratio_reads = sample2_reads / sample1_reads
    ratio_conc = sample1_conc / sample2_conc
    
    # Calculate additional amount of DNA needed for each sample
    additional_sample1 = max(0, (ratio_reads - 1) * sample1_amount)
    additional_sample2 = max(0, (1 - ratio_reads) * sample2_amount)
    
    return additional_sample1, additional_sample2, ratio_conc

def calculate_sample2_amount(sample1_amount, ratio_conc):
    """
    Calculate the amount of Sample 2 DNA needed based on the amount of Sample 1 DNA provided and the ratio of concentrations.

    Args:
        sample1_amount (float): Amount of Sample 1 DNA in ng.
        ratio_conc (float): Ratio of concentrations of Sample 1 and Sample 2 DNA.

    Returns:
        float: Amount of Sample 2 DNA needed in ng.
    """
    # Calculate amount of Sample 2 DNA needed
    sample2_amount = (ratio_conc * sample1_amount) / 21 * 21.4
    
    return sample2_amount
