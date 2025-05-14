import argparse
from modern_webapp_scraper.config import load_config
from modern_webapp_scraper.scraper import ModernWebAppScraper
from modern_webapp_scraper.storage import save_csv, save_json, save_sqlite


def main():
    parser = argparse.ArgumentParser(description="Modern Web Application Scraper")
    parser.add_argument('--config', default='../config.yaml')
    args = parser.parse_args()

    cfg = load_config(args.config)
    scraper = ModernWebAppScraper(cfg)
    rows = scraper.scrape()
    scraper.close()

    if not rows:
        print("No data extracted.")
        return

    fmt = cfg['storage']['formats']
    if 'csv' in fmt:
        path = save_csv(rows, list(rows[0].keys()), cfg['storage']['output_dir'])
        print(f"Saved CSV to {path}")
    if 'json' in fmt:
        path = save_json(rows, cfg['storage']['output_dir'])
        print(f"Saved JSON to {path}")
    if 'sqlite' in fmt:
        path = save_sqlite(rows, list(rows[0].keys()), cfg['storage']['output_dir'])
        print(f"Saved SQLite DB to {path}")

if __name__ == '__main__':
    main()