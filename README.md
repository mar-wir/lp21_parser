# Lehrplan 21 Kompetenzen Parser

## TL;DR:

- **Target users:** Any educational institution which operates under the swiss educational system and 'Lehrplan 21', but is not part of the public swiss school network, for example Swiss Schools in foreign countries.
- **Why?:** Lehrplan 21 is based on over 3000, cross-referenced skills, officially listed here: https://www.lehrplan21.ch/ . The website does not allow for a database export of those skills. Centralized planning of the coursework is hindered because of this. The current repo parses all those skills and exports them as csv file, thus enabling those organizations in their planning.
- **How?:** The csv file can be opened with a spreadsheet software (e.g. LibreOffice Calc or MS Excel) and skills, and cross references be searched and marked by teachers. If shared via google spreashseets, a centralized planning is possible. 
The csv file can also be used as basis for a database (e.g. mySQL) and paired with student information. Thus, the DB would hold real-time information on which student holds which skills, thus, making fine-grained course-planning attainable.

* * *

## What is this repo for?

The 'Lehrplan 21' is a new iteration of the Swiss education system, aiming at homogenizing education across all cantons (Swiss states). Previously bigger subjects have been split up into over 3000 small, granular skills (Kompetenzen, in german). Students will be awarded with those skills on fullfillment of a range of activities (exams, coursework etc.). There are Kompetenzen which are shared among different subjects, linked together via cross-references. This introduces some complexities into the organizaion and design of every teachers' coursework. With the current repository, teachers/schools are able to extract all Kompetenzen with their respective cross-references and use the resulting csv file as starting point for their planning. Below, a clearer illustration of the problem this repo attempts to address.

### The problem

Let's say you are teaching English class. You are currently deciding on which Kompetenzen you are going to address with your coursework. You are browsing the Lehrplan 21 website for your respective Canton. The Kompetenz [FS1E.3.C.1](https://sh.lehrplan.ch/index.php?code=a%7C1%7C21%7C3%7C3%7C1&hilit=1011349904418GrzVHbChC57ehEvEWJbA#1011349904418GrzVHbChC57ehEvEWJbA) (3.e 2, Canton Schaffausen) has caught your eye:

```
können einige Fehler, die beim freien Sprechen auftreten, erkennen und sich selber korrigieren.
```

This Kompetenz has two cross references: [D.1.C.1.e](https://sh.lehrplan.ch/index.php?code=a%7C1%7C11%7C1%7C3%7C1&hilit=101bt3PZ5rubxH6LxREd3M7TYryv4cDWM#101bt3PZ5rubxH6LxREd3M7TYryv4cDWM) and [D.3.B.1.e](https://sh.lehrplan.ch/index.php?code=a%7C1%7C11%7C3%7C2%7C1&hilit=101pD4KghZfFchU49ZaUhwJDALbDA9DxF#101pD4KghZfFchU49ZaUhwJDALbDA9DxF). They belong to two different areas of German: speaking and hearing. Without further meetings with your colleagues, you will not be able to plan your coursework guaranteeing that you are not addressing a Kompetenz which has already been covered or which is being covered at the same time in german class. Intensive centralized bookkeeping, paper-forms, or long planning sessions are traditional ways of coping with this added layer of difficulty. All cost and time intense approaches.

### Proposed Solution

Enabling live-tracking of which Kompetenz has been included in a teachers' coursework (for which students). The first step here is to extract all Kompetenzen from the official website (https://www.lehrplan21.ch/) and format the information as database-ready table (as much as the parsing allows it). There are several uses for such an extract:
- Use the csv file via a spreadsheet software (MS Excel, Google Sheets, OpenOffice Calc). Used Kompetenzen can be marked manually by teachers. If done collaborately on the cloud, this already serves its purpose in the planning.
- Include the csv file in a wider database (mysql, sql lite). Combine the Kompetenzen information with student information and track which student has covered which Kompetenzen. This solution is more invovled, but allows for personalized education. This approach furthermore requires the development of a front-end solution (for instance, Python Django/Flask or PHP Laravel/CakePHP). Naturally, a server is required to host those webapps. 

## Installation

- Install pip (Python dependency manager):

```bash
sudo apt-get install python3-pip
```

- Clone this repo and cd-in:

```bash
git clone git@github.com:Seneketh/lp21_parser.git

cd lp21_parser/dist/
```

- Install package and all dependencies:

By general rule, clone repo or pull latest changes before reinstalling. In the `dist` folder inside the repository:

```bash
sudo pip3 install lp21_parser*
```

- IF the package has already been installed previously and one wishes to update:

```bash
sudo pip3 install --upgrade --force-reinstall lp21_parser*
```

## Un-Install

```bash
sudo pip3 uninstall lp21_parser*
```
