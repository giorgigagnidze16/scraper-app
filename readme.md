# Modern Webapp Scraper

## Features

- **Authentication** (login forms, session cookies, text-CAPTCHA hooks)  
- **Pagination** & **infinite scroll** handling  
- **Dropdowns** & **filter clicks**  
- **Pre-scripts**: arbitrary JS to trigger lazy-load or manipulate the page  
- **Extraction** of 7+ data points per item, including nested elements and JS-computed values  
- **Locator strategies**: ID, Name, Class, Tag, CSS, XPath  
- **Post-processing**: normalize prices, dates, etc. via Python expressions  
- **Storage**: CSV, JSON, SQLite out of the box  
- **Retry logic** with exponential backoff  
- **CLI** entrypoint with configurable YAML  

## Directory Structure

```
scraper-app/
├── demo.yaml                # your configuration file
├── modern_webapp_scraper/
│   ├── __init__.py
│   ├── cli.py               # CLI entrypoint
│   ├── config.py            # YAML loader
│   ├── scraper.py           # main Selenium logic
│   ├── utils.py             # retries, delays, logging
│   └── storage.py           # CSV/JSON/SQLite writers
├── requirements.txt         # pip dependencies
└── outputs/                 # default output directory
```

## Prerequisites

- **Python 3.10+**  
- **Google Chrome** (or Firefox) and matching **WebDriver** on your `PATH`  
- (Optional) [`virtualenv`](https://docs.python.org/3/library/venv.html)  

## Installation

1. **Clone** the repo and enter the folder:
   ```bash
   git clone <your-repo-url>
   cd scraper-app
   ```
2. **Create** and **activate** a virtual environment (recommended):
   ```bash
   python -m venv .venv
   . .venv/Scripts/activate   # Windows
   # or
   source .venv/bin/activate  # macOS/Linux
   ```
3. **Install** dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration (`demo.yaml`)

Drop this file at `scraper-app/demo.yaml`. It targets [SauceDemo](https://www.saucedemo.com) and exercises login, filtering, JS execution, and extraction of multiple fields.

```yaml
# demo.yaml

target:
  url: "https://www.saucedemo.com/inventory.html"
  base_url: "https://www.saucedemo.com"
  login:
    enabled: true
    login_url: "https://www.saucedemo.com"
    credentials:
      username: "standard_user"
      password: "secret_sauce"
    selectors:
      username_field:
        type: css
        value: 'input[data-test="username"]'
      password_field:
        type: css
        value: 'input[data-test="password"]'
      submit_button:
        type: css
        value: 'input[data-test="login-button"]'
      captcha:
        enabled: false

navigation:
  max_pages: 1
  infinite_scroll: false
  dropdowns:
    - selector:
        type: css
        value: ".product_sort_container"
      action: select_by_value
      value: "lohi"
  filters:
    - selector:
        type: xpath
        value: "//input[@name='filter-checkbox']"
      action: click
  pre_scripts:
    - "window.scrollTo(0, document.body.scrollHeight);"

extraction:
  item_selector: ".inventory_item"
  fields:
    - name: product_name
      selector:
        type: css
        value: ".inventory_item_name"
      attribute: text
    - name: description
      selector:
        type: css
        value: ".inventory_item_desc"
      attribute: text
    - name: price
      selector:
        type: css
        value: ".inventory_item_price"
      attribute: text
      post_process: "float(re.sub(r'[^0-9.]','', value))"
    - name: image_url
      selector:
        type: css
        value: ".inventory_item_img img"
      attribute: src
    - name: button_text
      selector:
        type: css
        value: ".btn_inventory"
      attribute: text
    - name: button_data_test
      selector:
        type: css
        value: ".btn_inventory"
      attribute: "data-test"
    - name: product_link
      selector:
        type: css
        value: ".inventory_item_name"
      attribute: href
    - name: computed_color
      js: "return getComputedStyle(document.querySelector('.inventory_item_name')).color;"

storage:
  formats: ["csv", "json", "sqlite"]
  output_dir: "./outputs"

webdriver:
  browser: "chrome"
  headless: true
  implicit_wait: 10
  page_load_timeout: 30
  script_timeout: 30
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

retry:
  max_attempts: 3
  backoff_factor: 2
```

## Usage

From the project root (`scraper-app/`), run:

```bash
python -m modern_webapp_scraper.cli --config demo.yaml
```

- The scraper will **login**, navigate to the inventory page, apply filters/sorting, extract all configured fields, and write results to:
  - `./outputs/items.csv`
  - `./outputs/items.json`
  - `./outputs/items.sqlite`

## Customization

- **Change targets** by editing `target.url` or adding new `login` flows.  
- **Adjust pagination** via `navigation.max_pages` or turn on `infinite_scroll`.  
- **Add filters** or **dropdowns** under `navigation`.  
- **Extract new fields** by appending to `extraction.fields` (use CSS, XPath, or JS).  
- **Normalize** data with `post_process` Python expressions.  
- **Switch browsers** (to `"firefox"`) or toggle `headless` mode.  

## Troubleshooting

- **KeyError** on missing config keys? Make sure your YAML defines all required sections (`target.url`, `navigation.max_pages`, etc.).  
- **UnicodeDecodeError**? Ensure your config file is saved in **UTF-8**.  
- **WebDriver errors**? Check that your browser and WebDriver versions match and are on your `PATH`.  
- **Selectors not found**? Inspect the live page and adjust your `type`/`value` under `selectors` or `fields`.  
