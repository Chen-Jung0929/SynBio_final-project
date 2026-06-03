import urllib.request, json
genes = ['APLP2', 'ATP5J2', 'C19orf33', 'COX6A1', 'CSTB', 'CYBA', 'EZR', 'FXYD3', 'GPRC5A', 'GPX1', 'GSTP1', 'HLA-A', 'HLA-B', 'IFI27', 'ITGB4', 'KRT18', 'KRT8', 'LGALS4', 'LYZ', 'OCIAD2', 'PERP', 'S100A14', 'S100A16', 'S100A6', 'SAT1', 'SH3BGRL3', 'SMIM22', 'SPINT2', 'TMC5', 'TSPAN8', 'UQCRQ', 'YWHAZ']
url = 'https://mygene.info/v3/query'
data = json.dumps({'q': ','.join(genes), 'scopes': 'symbol', 'fields': 'ensembl.gene', 'species': 'human'}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read())
    mapping = {}
    for r in res:
        if 'ensembl' in r:
            ens = r['ensembl']
            if isinstance(ens, list): ens = ens[0]
            if 'gene' in ens:
                mapping[ens['gene']] = r['query']
    print(json.dumps(mapping))
except Exception as e:
    print(e)
