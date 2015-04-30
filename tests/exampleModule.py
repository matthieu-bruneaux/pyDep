def fib(n) :
    assert type(n) == int
    if n == 0 or n == 1 :
        return(1)
    else :
        return fib(n-1) + fib(n-2)

def sensibleFib(n) :
    if n < 20 :
        return fib(n)
    else :
        raise Exception("n is too large")

def makeDNAcomplement(dnaString) :
    validateDNAstring(dnaString)
    dnaComplementDict = {"A" : "T", "T" : "A", "G" : "C", "C" : "G"}
    complement = ""
    for nt in dnaString :
        complement += dnaComplementDict[nt]
    return complement

def makeDNAreverseComplement(dnaString) :
    validateDNAstring(dnaString)
    complement = list(makeDNAcomplement(dnaString))
    complement.reverse()
    return("".join(complement))

def validateDNAstring(dnaString) :
    if not isValidDNAstring(dnaString) :
        raise Exception("Not a valid DNA string")

def isValidDNAstring(dnaString) :
    allowedChar = "ATGC"
    return(all([x in allowedChar for x in dnaString]))

def transcribeDNA(dnaString) :
    validateDNAstring(dnaString)
    transcript = makeDNAcomplement(dnaString)
    transcript = transcript.replace("T", "U")
    return(transcript)

def simpleFunc(x) :
    return x

def evenSimplerFunc(x) :
    pass

