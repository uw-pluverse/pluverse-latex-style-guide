# A  short tutorial for drawing figures using PowerPoint


## Save Images to PDF

If you are using Mac:

1. Go to the slide,
2. Select the components that compose your figure, or just press CMD + A.
3. Right-click on the components and select "Save as picture"
4. In the dialog box, choose "PDF" in the "Save as Type".
5. Click "save" to save the file.

If you are using Windows, the above way does not work for you since there is no "PDF" when you choose "save as picture"

(This way is also applicable for Mac)
1. Click "File" in the left-up corner
2. Choose "Export" -- "Create PDF/XPS Document"
3. In the dialog, the "Option" will allow you to select which pages to be saved.
4. Make sure you choose "PDF" in "Save as type" and click publish.


There are some differences between the above approach.
The first way only exports the region of the components you selected
and the size of the exported PDF is determined by your components.
The second method exports the entire page and the size is fixed.
You may need to trim or crop the image, using Preview or Latex.

```
\includegraphics[trim={5cm 0 0 0},clip]{example-image-a}
```


## Some suggestions.

There are many ways to draw a figure. Here are some general suggestions.

1. Make the figure clear and easy to follow.
2. Use arrows and numbers to guide the readers to understand your figure.
3. Consider using dotted/dashed/solid lines when necessary.
4. Avoid having intersecting lines.
5. Add a label for each component and make sure it is simple and consistent with the terms used in your paper.
6. Use some simple colors when your draw a figure.
7. Make sure the figure is printing-friendly, especially for mono printing.
8. The font should be Times New Roman. The size should be around 20.
9. Double-check if the figure is still good after it is included in latex.

## Code in figures

You can copy the code from VS code or similar IDEs and then paste them into slides.
The syntax highlighting will be preserved.