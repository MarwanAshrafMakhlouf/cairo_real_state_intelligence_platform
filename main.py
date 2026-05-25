from src import scraper
from src import scrape_links
from src import cleaning
def main():
    print("Hello from cairo-real-state-intelligence-platform!")
    # scraper.main()
    scraper.main()
    cleaning.main()


if __name__ == "__main__":
    main()
