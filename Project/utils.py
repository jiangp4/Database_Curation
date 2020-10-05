
def parse_keywords(keywords, sep = ',', white_space='[-_. ]?', flag_Chrome=False, flag_addstart=False):
    results = []
    
    keywords = keywords.split('\n')

    # keywords must start with non digit and characters
    if flag_addstart:
        if flag_Chrome:
            # look behind only in Chrome
            pattern = '(^|(?<=[^a-z0-9]))%s'
        else:
            pattern = '(^|[^a-z0-9])%s'
    else:
        pattern = '%s'
    
    for l in keywords:
        l = l.replace('\n','').replace('\r','').strip().strip(sep)
        if len(l) == 0 or l[0] in ['#']: continue
        
        lst = l.split(sep)
        
        for v in lst:
            v = v.strip()
            if white_space is not None: v = pattern % v.replace(' ', white_space)
            
            results.append(v)
    
    return sep.join(results)
