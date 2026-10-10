from pathlib import Path
import json,re
base=Path(__file__).resolve().parents[1]
pages=json.loads((base/'report-content.json').read_text())
def esc(s):
 mapping={'–':'--','—':'---','’':"'",'‘':"'",'“':'``','”':"''",'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}','−':r'\ensuremath{-}','≤':r'\ensuremath{\leq}','×':r'\ensuremath{\times}','→':r'\ensuremath{\rightarrow}','µ':r'\ensuremath{\mu}','²':r'\textsuperscript{2}'}
 s=re.sub(r'([0-9a-f]{40,64})',lambda m:' '.join(m[0][i:i+8] for i in range(0,len(m[0]),8)),s)
 return ''.join(mapping.get(c,c) for c in s)
s=[r'''\documentclass[10pt,letterpaper]{article}
\usepackage[margin=0.75in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{graphicx,array,longtable,booktabs,xcolor}
\usepackage{fancyvrb}
\usepackage[hidelinks]{hyperref}
\usepackage{microtype}
\usepackage{caption}
\newcommand{\reportimage}[2]{\IfFileExists{#2}{\includegraphics[width=#1in,height=3.3in,keepaspectratio]{#2}}{\fbox{\parbox[c][1in][c]{0.9\linewidth}{\centering Figure asset: \texttt{\detokenize{#2}}\\The standalone preview cannot load companion images.\\Compile the complete source package to display this figure.}}}}
\definecolor{reportblue}{HTML}{244B62}
\hypersetup{pdftitle={TinySystolic technical report},pdfauthor={Krishna Chemudupati}}
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt}
\setlength{\emergencystretch}{3em}
\renewcommand{\arraystretch}{1.18}
\begin{document}
''']
for i,page in enumerate(pages):
 if i:s.append(r'\clearpage')
 title=page['title']
 if i==0:s.append(r'{\LARGE\bfseries '+esc(title)+r'\par}\vspace{8pt}')
 else:s.append(r'\section{'+esc(re.sub(r'^\d+\s+','',title))+r'}')
 for b in page['blocks']:
  if b[0]=='p':s.append(esc(b[1]).replace('\n',r'\\')+'\n')
  elif b[0]=='h2':s.append(r'\subsection*{'+esc(b[1])+'}')
  elif b[0]=='code':s.append(r'\begin{quote}\ttfamily\small '+esc(b[1]).replace('\n',r'\\'+'\n')+r'\end{quote}')
  elif b[0]=='table':
   _,heads,rows,widths=b
   weights=widths or [1]*len(heads);total=sum(weights)
   cols=''.join(r'>{\raggedright\arraybackslash}p{'+f'{w/total:.6f}'+r'\dimexpr\linewidth-'+str(2*len(heads))+r'\tabcolsep\relax}' for w in weights)
   s.append(r'{\small\begin{longtable}{'+cols+'}'+r'\toprule')
   header=' & '.join(r'\textbf{'+esc(h)+'}' for h in heads)+r'\\\midrule'
   s.append(header+r'\endfirsthead'+header+r'\endhead')
   s.extend(' & '.join(esc(c) for c in row)+r'\\' for row in rows)
   s.append(r'\bottomrule\end{longtable}}')
  elif b[0]=='figure':
   _,name,cap,width=b
   path=(base/'figures'/name).resolve().relative_to(base)
   caption=re.sub(r'^Figure \d+\s+','',cap)
   s.append(r'\begin{center}\reportimage{'+str(min(width,6.5))+r'}{'+str(path)+r'}\captionof{figure}{'+esc(caption)+r'}\end{center}')
  elif b[0]=='link':s.append(r'\href{'+b[2]+r'}{'+esc(b[1])+r'}\par')
s.append(r'\end{document}')
(base/'TinySystolic_Technical_Report.tex').write_text('\n'.join(s)+'\n')
print('LaTeX generated with all narrative, tables, and 11 figures')
