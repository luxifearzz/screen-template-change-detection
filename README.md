## How To Use (for Windows)

- Has python installed
- Create virtual environment and activated it using

```bash
python -m venv .venv
.venv\Scripts\activate
```

- Install required lib using

```bash
python -m pip install -r requirements.txt
```

- Import template image you want to detect it's position to `images/templates/` folder & named it `initial.png`.
- Import template image of goal state to `images/templates/` folder & named it `finished.png`.
- (Handle 2 option cases) Import template image of cases that might be found in the process to `images/templates/` folder & named it `option_a.png` and `option_b.png`. Program will find coordinates of those option and auto clicked them.
- Run the program using `run.bat` file (for Windows).
