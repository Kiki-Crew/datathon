import nbformat

path = "/Users/nano/Desktop/데이터톤/datathon/딥러닝_및_전통ML_BERTopic.ipynb"
nb = nbformat.read(path, as_version=4)

nb.metadata.pop("widgets", None)

nbformat.write(nb, path)