\ProvidesClass{cv}

\LoadClass{article}

\RequirePackage[dvipsnames,x11names]{xcolor}
\RequirePackage{xhfill}
\RequirePackage[hidelinks]{hyperref}
\RequirePackage{fontawesome}
\RequirePackage{fontenc}
\RequirePackage{etoolbox}
\RequirePackage{changepage}

\RequirePackage{geometry}
\geometry{
	left=.5in,
	right=.5in,
	top=.5in,
	bottom=.5in,
	footskip=1.5em,
}

\colorlet{sectionColor}{black}

\RequirePackage[
	maxnames=100,
	sorting=none,
	style=authortitle,
	dashed=false,
]{biblatex}
\addbibresource{publications.bib}
\setlength\bibitemsep{1.2\itemsep}
\DeclareNameAlias{default}{given-family}
\DeclareNameAlias{sortname}{given-family}

\RequirePackage{parskip}
\pagestyle{empty}
\raggedright

\RequirePackage[explicit]{titlesec}

\titleformat{\section}
{\Large \scshape}
{}
{0em}  % number-header spacing 
{\color{sectionColor} #1 \ \xrfill[.2em]{.2pt}}

\titleformat{\subsection}[runin]
{}
{}
{0em}  % number-header spacing 
{#1}

% leading, before, after
\titlespacing{\section}{0em}{1em}{.5em}
\titlespacing{\subsection}{1em}{.2em}{.1em}

\RequirePackage{enumitem}
\newcommand{\bulletpoint}{\raisebox{0.2em}{\rule{0.5ex}{0.5ex}}}
\setlist{
	nosep,
	leftmargin=2.5em,
	rightmargin=2em,
	itemsep=3pt,
	label={\bulletpoint},
}
\AtEndEnvironment{itemize}{\vspace{.8em}}
\AtBeginEnvironment{itemize}{\vspace{-.3em}}

\RequirePackage{ifthen}
\RequirePackage{fancyhdr}
\RequirePackage{lastpage}
\pagestyle{fancy}
\renewcommand{\headrulewidth}{0pt} % remove line from header
\fancyhf{} % clear header and footer
\cfoot{
	\color{gray}
	\footnotesize
	\itshape
	\ifthenelse{\pageref{LastPage}=1}{}{Page \thepage\ of \pageref{LastPage}.}
	Compiled \today.
}

\linespread{1.05}

