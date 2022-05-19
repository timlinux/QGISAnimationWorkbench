# Working with documentation

Documentation is written using [mkdocs](https://mkdocs.org/).

## Building documentation PDF

You can build a copy of the documentation as a PDF file using the following steps:

```bash
pip install mkdocs-with-pdf
pip install mkdocs-material
pip install qrcode
mkdocs build
xdg-open pdfs/QGISAnimationPlugin.pdf 
```
