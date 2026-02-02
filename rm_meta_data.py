import nbformat

path = "[파일 경로]"
nb = nbformat.read(path, as_version=4)

nb.metadata.pop("widgets", None)

nbformat.write(nb, path)
