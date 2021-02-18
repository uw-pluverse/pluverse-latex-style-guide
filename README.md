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

## Capitalize the caption for meaningful word.

The first word in caption of Table/Figure should be capitalized, but not for preposition and conjunction word. 

For example, it should be `The Effectiveness of ADF in Three Datasets`.

## Always use vector graphs and use the right font in the graphs.

- Try to avoid using `.png`, `.jpg` and `.bmp`, because they look blury when zoomed in.

- Always use `.eps` or `.pdf`.

- Make sure the font in the figure is the same font.

## Carefully select the color and the markers in the figure. 

The color and markers of figures, especially for the line chart and bar chart, should be able to distinguished even in black-white printing.
This website can help you pick color https://learnui.design/tools/data-color-picker.html

## Use booktab table style. 

For table, you can use this website.https://www.tablesgenerator.com/. Now it is more common to use the "booktab table style".

## Write numbers in words.

If you use numbers such as `1`, `2`, `100`, and `1000`, you should write `one`, `two`, `one hundred`, and `one thousand`.
If you use number such as `2021`, it should write it as `2,021`

More information can be found [here](https://www.dcu.ie/sites/default/files/students_learning/docs/WC_Numbers-in-academic-writing.pdf)

## Try to use bib files from ACM Digitial Library and IEEE Xplore.

Avoid the citation from arxiv, if possile.

## Use language tool to check the grammar.

If you are using Texstudio, please follow this:  https://tex.stackexchange.com/a/282571.

## Quote.

Single quotation marks are produced in LaTeX using  ` and  '.

Double quotation marks are `` and ''.

For example

```tex
`Something'
``The title of this paper is hope''
```



## Other files in this repo
`comment_macror.tex`, to leave comments
`auto_counter_macro.tex`,  If you have a lot of findings/reponses, you can use the following commands to automatic generate counters.
`abbr_macros.tex`, macro for common macros.
