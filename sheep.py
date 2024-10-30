import matplotlib.pyplot as plt
import pandas as pd
import requests

from io import BytesIO


def download_data(gene, dataset='cell_RNA_pancreatic_cancer', cell_lines=None,
    thpa_url='http://www.proteinatlas.org/'):
    # Use the HPA API to request the chosen gene and dataset
    r = requests.get(f'{thpa_url}api/search_download.php?'
        f'search={gene}&format=tsv&columns=g,gs,{dataset}&compress=no')
    # Convert into pandas DataFrame
    data = pd.read_csv(BytesIO(r.content), sep='\t')
    # Modify column names from 'RNA expression - cell type [nTPM]'
    # to just 'cell type'
    data.columns = [x.split('[')[0].split(' - ')[1].strip() if 'RNA' in x 
        else x for x in data.columns]
    # If cell lines are not specified, just use all of them
    if cell_lines is None:
        # First two columns are 'Gene' and 'Gene synonym'
        cell_lines = [i for i in data.columns[2:]]
    # Choose only exact matches (API gives more)
    index = data[data['Gene'] == gene].index
    # If no exact matches
    if len(index) == 0:
        print (f'Gene {gene} not found by name, trying by gene synonym')
        # Search for the provided gene name in gene synonyms
        index = data[data['Gene synonym'].apply(lambda x: gene in x.split(', ') 
            if type(x) == str else False)].index
        # If no matches still
        if len(index) == 0:
            print (f'Gene {gene} not found by name or synonym')
            return pd.DataFrame(columns=cell_lines)
    # If more than one exact match (possibly after rematching)
    if len(index) > 1:
        print (f'More than one match found for gene {gene},'
            'using the first one')
        print ('You may want to refine your query')
    # Choose the first index in the list (may be the only one)
    ind = index[0]   
    # Return the relevant data
    return data.loc[ind, cell_lines]


FIG_HEIGHT = 4
FIG_WIDTH_PER_COL = 0.8 

def generate_gene_image(gene, dataset='cell_RNA_pancreatic_cancer',
    bg_dataset=None, cell_lines=None, figsize=None, sort=False, save_to=None):
    # Download the cell line data for the gene
    to_plot = download_data(gene, dataset, cell_lines)
    # Check any data was received
    if len(to_plot) == 0:
        print ('No rows in the dataframe for plotting')
        return plt.subplots()
    # Download the background data if required
    if bg_dataset is not None:
        bg_data = download_data(gene, bg_dataset)
    # Sort by expression descending if required
    if sort:   
        to_plot.sort_values(inplace=True, ascending=False)
    # Calculate a default figure size if one was not provided
    if figsize is None:
        figsize = (FIG_WIDTH_PER_COL*len(to_plot),FIG_HEIGHT)
    # Generate a figure
    fig, ax = plt.subplots(figsize=figsize)
    # Positions for the bars on the plot
    positions = [i for i in range(len(to_plot))]
    ax.bar(positions, to_plot.values)
    # Adjust figure properties
    ax.set_title(gene)
    ax.set_xlim(-0.5, len(to_plot)-0.5)
    ax.set_ylabel('RNA expression / nTPM')
    # Add the background line if required
    if bg_dataset is not None:
        # Get the current limits of the x axis
        x_range = ax.get_xlim()
        # Plot the line using the background data
        ax.plot(x_range, [bg_data.values[0]]*2, 'r--', lw=2)
        # Restore the old limits
        ax.set_xlim(x_range)
    # Add the appropriately rotated cell type labels
    ax.set_xticks(positions, to_plot.index, rotation=90, ha='center')
    # Save to a file if required
    if save_to is not None:
        fig.savefig(save_to, dpi=300, bbox_inches='tight')
    # Return the Figure and Axes handles for further manipulation
    return fig, ax