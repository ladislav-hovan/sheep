import pytest

import matplotlib.pyplot as plt

from sheep.sheep import generate_gene_image

@pytest.mark.parametrize('input', [
    dict(gene='ERBB2'),
    dict(gene='ERBB2', dataset='cell_RNA_breast_cancer'),
    dict(gene='ERBB2', dataset='cell_RNA_breast_cancer',
        cell_lines=['HCC1419', 'MX-1']),
])
def test_generate_gene_image(input):
    fig,_ = generate_gene_image(**input)

    assert type(fig) == plt.Figure