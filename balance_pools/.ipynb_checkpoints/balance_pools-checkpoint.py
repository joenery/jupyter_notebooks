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
        None: The function prints out the additional amount of DNA needed for each sample.

    Note:
        The function assumes that the ratio of reads directly corresponds to the ratio of DNA amounts added.
        It also assumes that the ratio of DNA concentrations is inversely proportional to the ratio of DNA amounts added.
    """
    print("Calculating ratios")
    # Calculate ratios
    ratio_reads = sample2_reads / sample1_reads
    ratio_conc = sample1_conc / sample2_conc
    print(ratio_reads)
    print(ratio_conc)
    # Calculate excess/deficit of DNA
    excess_sample1 = sample1_amount - (ratio_conc * sample2_amount)
    excess_sample2 = sample2_amount - (sample1_amount / ratio_conc)
    print(excess_sample1)
    print(excess_sample2)

    # Check if adjustments are needed
    if excess_sample1 > 0:
        print("No more Sample 1 DNA needs to be added.")
    if excess_sample2 > 0:
        print("No more Sample 2 DNA needs to be added.")

    # Calculate additional amount of DNA needed
    if excess_sample1 < 0:
        additional_sample1 = abs(excess_sample1)
        print(f"Additional {additional_sample1} ng of Sample 1 DNA needed.")
    if excess_sample2 < 0:
        additional_sample2 = abs(excess_sample2)
        print(f"Additional {additional_sample2} ng of Sample 2 DNA needed.")

sample1_reads = 658726
sample2_reads = 1315592
sample1_amount = 17.9
sample2_amount = 21
sample1_conc = 17.9
sample2_conc = 21

calculate_additional_DNA(sample1_reads, sample2_reads, sample1_amount, sample2_amount, sample1_conc, sample2_conc)

