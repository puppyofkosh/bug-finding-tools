
# Makes a binary spectrum
def make_spectrum_from_trace(trace):
    spectrum = {line: 1 if count > 0 else 0
                for line, count in trace.iteritems()}
    return spectrum

#def get_ranks_from_spectrum(spectrum):
    
