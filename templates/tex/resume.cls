\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ali-resume}

\LoadClass[10pt]{article}

\RequirePackage{geometry}
\RequirePackage[explicit]{titlesec}
\RequirePackage{xhfill}
\usepackage{ifthen}
\RequirePackage{parskip}
\RequirePackage[colorlinks]{hyperref}
\RequirePackage{fontawesome}
\RequirePackage[T1]{fontenc}

% citations
\RequirePackage[maxnames=100, giveninits=true]{biblatex}
\addbibresource{publications.bib}

% -- MARGINS --

\geometry{margin=4em}
\pagestyle{empty}  % remove page numbering

% -- LISTS --

\RequirePackage{enumitem}

\setlist[itemize]{
	label={\bfseries-},
	leftmargin=1.5em,
	topsep=-.1em,
	itemsep=-.3em,
}

%  -- TITLE --
\makeatletter
\renewcommand{\maketitle}{
\setlength{\leftskip}{-1em}

{\huge \scshape \@author}

\vspace{-.5em}
\rule{.4 \textwidth}{0.5pt}

{
{\it \phone}
\ | \
{\it \email}
\ | \
\href{http://\website}{\it \website}
}

\setlength{\leftskip}{0em}
}
\makeatother

% -- SECTION --

\titlespacing{\section}
{-1em}  % leading
{.8em}  % before
{.4em}  % after

\titleformat{\section}
{}
{}
{0em}  % number-header spacing 
{\Large \scshape  #1 \ \xrfill[.2em]{.5pt}}

% -- RESUME ITEM --

\titlespacing{\subsection}
{0em}  % leading
{1em}  % before
{.5em}  % after

\titleformat{\subsection}
{}
{}
{0em}  % number-header spacing 
{\bfseries #1}

\newcommand{\resumeitem}[3]{\subsection{%
		\def\subtitle{#2}%
		\def\empty{}%
		#1%
		\ifx\subtitle\empty{ }\else{, }\fi
		{\normalfont \itshape #2}
		\hfill
		{\normalfont \itshape #3}
	}}


% -----------
% -- LINKS -- 
% -----------

\let\oldhref\href
\renewcommand{\href}[2]{%
	#2
	\oldhref{#1}{\raisebox{-.1em}{\faicon{link}}}%
}

