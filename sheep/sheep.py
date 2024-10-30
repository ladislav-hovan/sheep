### Imports ###
import pandas as pd
import matplotlib.pyplot as plt
import requests

from typing import Optional, Iterable, Tuple

from io import BytesIO

### Functions ###
def download_data(
    gene: str, 
    dataset: str = 'cell_RNA_pancreatic_cancer', 
    cell_lines: Optional[Iterable[str]] = None
) -> pd.DataFrame:
    """
    Queries the Human Protein Atlas API to retrieve expression data 
    for a given gene from one of their datasets. The data are then 
    optionally filtered to only include the cell lines provided.

    Parameters
    ----------
    gene : str
        The name of the gene of interest
    dataset : str, optional
        The dataset to retrieve the data from, by default 
        'cell_RNA_pancreatic_cancer'
    cell_lines : Optional[Iterable[str]], optional
        The iterable with the names of the cell lines of interest or 
        None to use all available ones, by default None

    Returns
    -------
    pd.DataFrame
        The retrieved and filtered pandas DataFrame
    """

    # Use the HPA API to request the chosen gene and dataset
    r = requests.get('http://www.proteinatlas.org/api/search_download.php?'
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


def generate_gene_image(
    gene: str, 
    dataset: str = 'cell_RNA_pancreatic_cancer', 
    bg_dataset: Optional[str] = None, 
    cell_lines: Optional[Iterable[str]] = None, 
    figsize: Optional[Tuple[float, float]] = None, 
    sort: bool = False, 
    save_to: Optional[str] = None
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Generates a bar plot of expression levels for a gene in different
    cell types based on data retrieved from the Human Protein Atlas.
    Can also sort the data by expression and add a background level
    corresponding to healthy tissue. The resulting figure can be saved.

    Parameters
    ----------
    gene : str
        The name of the gene of interest
    dataset : str, optional
        The dataset to retrieve the data from, by default 
        'cell_RNA_pancreatic_cancer'
    bg_dataset : Optional[str], optional
        The dataset to retrieve the background data from or None to not
        include any background, by default None
    cell_lines : Optional[Iterable[str]], optional
        The iterable with the names of the cell lines of interest or 
        None to use all available ones, by default None
    figsize : Optional[Tuple[float, float]], optional
        The tuple with the figure dimensions or None to use an estimate 
        based on the number of cell lines, by default None
    sort : bool, optional
        Whether to sort the values by expression descending, 
        by default False
    save_to : Optional[str], optional
        The file path for saving or None to not save, by default None

    Returns
    -------
    Tuple[plt.Figure, plt.Axes]
        The resulting Figure and Axes objects
    """

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
        figsize = (0.8*len(to_plot),4)
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