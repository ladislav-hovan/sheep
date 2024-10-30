import matplotlib.pyplot as plt
import pandas as pd
import requests

from io import BytesIO


def download_data(gene, dataset='cell_RNA_pancreatic_cancer', cell_lines=None,
    thpa_url='http://www.proteinatlas.org/'):
    r = requests.get(f'{thpa_url}api/search_download.php?'
        f'search={gene}&format=tsv&columns=g,gs,{dataset}&compress=no')
    data = pd.read_csv(BytesIO(r.content), sep='\t')
    data.columns = [x.split('[')[0].split(' - ')[1].strip() if 'RNA' in x 
        else x for x in data.columns]
    if cell_lines is None:
        cell_lines = [i for i in data.columns[2:]]
    index = data[data['Gene'] == gene].index
    if len(index) == 0:
        print (f'Gene {gene} not found by name, trying by gene synonym')
        index = data[data['Gene synonym'].apply(lambda x: gene in x.split(', ') 
            if type(x) == str else False)].index
        if len(index) == 0:
            print (f'Gene {gene} not found by name or synonym')
            return pd.DataFrame(columns=cell_lines)
    if len(index) > 1:
        print (f'More than one match found for gene {gene},'
            'using the first one')
        print ('You may want to refine your query')
    ind = index[0]   

    return data.loc[ind, cell_lines]


FIG_HEIGHT = 4
FIG_WIDTH_PER_COL = 0.8 

def generate_gene_image(gene, dataset='cell_RNA_pancreatic_cancer',
    bg_dataset=None, cell_lines=None, figsize=None, sort=False, save_to=None):
    to_plot = download_data(gene, dataset, cell_lines)
    if len(to_plot) == 0:
        print ('No rows in the dataframe for plotting')
        return plt.subplots()
    if bg_dataset is not None:
        bg_data = download_data(gene, bg_dataset)
    if sort:   
        to_plot.sort_values(inplace=True, ascending=False)
    if figsize is None:
        figsize = (FIG_WIDTH_PER_COL*len(to_plot),FIG_HEIGHT)
    fig, ax = plt.subplots(figsize=figsize)
    positions = [i for i in range(len(to_plot))]
    ax.bar(positions, to_plot.values)
    ax.set_title(gene)
    ax.set_xlim(-0.5, len(to_plot)-0.5)
    ax.set_ylabel('RNA expression / nTPM')
    if bg_dataset is not None:
        x_range = ax.get_xlim()
        ax.plot(x_range, [bg_data.values[0]]*2, 'r--', lw=2)
        ax.set_xlim(x_range)
    ax.set_xticks(positions, to_plot.index, rotation=90, ha='center')
    if save_to is not None:
        fig.savefig(save_to, dpi=300, bbox_inches='tight')

    return fig, ax