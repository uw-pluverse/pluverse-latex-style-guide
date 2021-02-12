## Short Column Width

Keep a line short. I would recommend to break a line at 60. The benefits of doing this are

- Friendly to version control system. Easy to diff. 
- Better bi-directional mapping between the output pdf file and the latex source.
- Friendly to the editor. No need to use the editor's wrapping functionality.

## Decompose a single BIG .tex file into multiple .tex files

- Friendly to version control system. Easy to diff. Minimize merge conflicts.
- Better organization of the paper, for example, each section is in its own file.

## Have a main.tex file

- Easy to identify the entry of the tex project.

## Use '~' between the words and '\cite', and '\ref'.

This allows the citation or the figure label to stay together with the previous word with a whitespace in between.

- `A and B developed a new approach~\cite{paper-id}`
- `Figure~\ref{figure-label} shows the overall framework.`

## Put captions above tables, and below figures.

This applies to most of the proceeding formats.

## Always use vector graphs and use the right font in the graphs.

- Try to avoid using `.png`, `.jpg` and `.bmp`, because they look blury when zoomed in.

- Always use `.eps` or `.pdf`.

- Make sure the font in the figure is the same font.
