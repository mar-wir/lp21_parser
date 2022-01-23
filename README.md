[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

# Lehrplan 21 Kompetenzen Parser

## TL;DR:

- **Target users:** Any educational institution which operates under the Swiss educational system and 'Lehrplan 21', but is not part of the public Swiss school network, for example Swiss Schools in foreign countries.
- **Why?:** Lehrplan 21 is based on over 3000, cross-referenced skills, officially listed here: https://www.lehrplan21.ch/ . The website does not allow for a database export of those skills. Centralized planning of the coursework is hindered because of this. The current repo parses all those skills and exports them as csv file, thus enabling those organizations in their planning.
- **How?:** Download the Kompetenzen export for your Kanton [here](https://github.com/Seneketh/lp21_parser/releases/tag/v0.5.0). The csv file can be opened with a spreadsheet software (e.g. LibreOffice Calc or MS Excel) and skills, and cross references be searched and marked by teachers. If shared via google spreadsheets, a centralized planning is possible. The csv file can also be used as basis for a database (e.g. mySQL) and paired with student information. Thus, the DB would hold real-time information on which student holds which skills, thus, making fine-grained course-planning attainable.

* * *

## What is this repo for?

The 'Lehrplan 21' is a new iteration of the Swiss education system, aiming at homogenizing education across all cantons (Swiss states). Previously bigger subjects have been split up into over 3000 small, granular skills (Kompetenzen, in German). Students will be awarded with those skills on fullfillment of a range of activities (exams, coursework etc.). There are Kompetenzen which are shared among different subjects, linked together via cross-references. This introduces some complexities into the organizaion and design of every teachers' coursework. With the current repository, teachers/schools are able to extract all Kompetenzen with their respective cross-references and use the resulting csv file as starting point for their planning. Below, a clearer illustration of the problem this repo attempts to address.

### The problem

Let's say you are teaching English class. You are currently deciding on which Kompetenzen you are going to address with your coursework. You are browsing the Lehrplan 21 website for your respective Canton. The Kompetenz [FS1E.3.C.1](https://sh.lehrplan.ch/index.php?code=a%7C1%7C21%7C3%7C3%7C1&hilit=1011349904418GrzVHbChC57ehEvEWJbA#1011349904418GrzVHbChC57ehEvEWJbA) (3.e 2, Canton Schaffausen) has caught your eye:

```text
können einige Fehler, die beim freien Sprechen auftreten, erkennen und sich selber korrigieren.
```

This Kompetenz has two cross references: [D.1.C.1.e](https://sh.lehrplan.ch/index.php?code=a%7C1%7C11%7C1%7C3%7C1&hilit=101bt3PZ5rubxH6LxREd3M7TYryv4cDWM#101bt3PZ5rubxH6LxREd3M7TYryv4cDWM) and [D.3.B.1.e](https://sh.lehrplan.ch/index.php?code=a%7C1%7C117C3%7C2%7C1&hilit=101pD4KghZfFchU49ZaUhwJDALbDA9DxF#101pD4KghZfFchU49ZaUhwJDALbDA9DxF). They belong to two different areas of German: speaking and hearing. Without further meetings with your colleagues, you will not be able to plan your coursework guaranteeing that you are not addressing a Kompetenz which has already been covered or which is being covered at the same time in German class. Intensive centralized bookkeeping, paper-forms, or long planning sessions are traditional ways of coping with this added layer of difficulty. All cost and time intense approaches.

### Proposed Solution

Enabling live-tracking of which Kompetenz has been included in a teachers' coursework (for which students). The first step here is to extract all Kompetenzen from the official website (https://www.lehrplan21.ch/) and format the information as database-ready table (as much as the parsing allows it). There are several uses for such an extract:

- Use the csv file via a spreadsheet software (MS Excel, Google Sheets, OpenOffice Calc). Used Kompetenzen can be marked manually by teachers. If done collaboratively on the cloud, this already serves its purpose for the planning.
- Include the csv file in a wider database (mysql, sql lite). Combine the Kompetenzen information with student information and track which student has covered which Kompetenzen. This solution is more involved, but allows for personalized education. This approach furthermore requires the development of a web-app solution (for instance, Python Django/Flask or PHP Laravel/CakePHP). Naturally, a server is required to host those web-apps.

### Download of the Kompetenzen

I already made exports for several Cantons. If there is interest, I can export others. Below, instruction on how export the Kompetenzen on your own.

### :sparkles: [**Downloads here**](https://github.com/Seneketh/lp21_parser/releases/tag/v0.5.0) :sparkles:

# DIY for devs

If the result of the export is not what your were looking for, or you want to do the exports on your own, below a guide on how to get the parser working on your machine. Pull requests are always welcome, of course.

## Simple Installation just by cloning the repo

Instead of installing the package via pip, just clone this repo and launch the parser invoking the script directly (see below). This means you either install all dependencies manually or use a virtualenv. I recommend `poetry`, as I already set the environment up via that approach.

Pre-requisite: Package manager `Poetry`.

Clone the repository:

```bash
git clone git@github.com:Seneketh/lp21_parser.git
cd lp21_parser/
```

Create virtualenv and install all packages and dependencies:

```bash
poetry install
```

Optional (and sometimes slow):

```bash
poetry update
```

Activate the virtual environment:

```bash
poetry shell
```

Install all and set up all pre-commit hooks:

```bash
pre-commit install
```

Check the python version. Note, use `python`, not `python3`, you still should get a python >3.6 version:

```bash
python --version
```

Make the call:

```bash
python Parser.py <arg1>
```

- `arg1` need be the desired canton, such as 'ag'. The default value is 'sh'. The exact string is the shorthand for each canton.

Example:

```bash
python Parser.py 'zh'
```

To exit the virtual environment:

```bash
exit
```

## Un-Installs

If you just cloned the repo, delete the directory. Don´t forget to remove the virtual environment created by poetry with `poetry env remove`.

### Poetry installation quick-guide:

For MacOS, Linux, and WSL:

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3
```

To apply changes for your current shell session, run

```bash
source $HOME/.poetry/env
```

You may add this to the auto-run shell script like .bashrc or .zshrc if Poetry doesn’t appear in a new shell session:

```bash
export PATH="$HOME/.poetry/bin:$PATH"
```

## Disclaimers and Licence

If intended, the present piece of software can be used to disrupt normal traffic on its target website. I discourage any use other than to facilitate and/or improve coursework planning of the eligible educational institutions. The present software is available under the `Attribution-NonCommercial-ShareAlike 4.0 International` licence. This means you can alter/adapt/improve the present code however you like and make free use of it, as long as you cite this repo as origin and DO NOT use it for COMMERCIAL APPLICATIONS. It is included in full under "LICENCE" in this repository. To my knowledge, there are no laws in Switzerland which impede the intended use of the present software.
