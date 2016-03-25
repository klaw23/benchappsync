from sportability import Sportability

def main():
    sportability = Sportability(42178, 279958, 'Hockey Moms')
    sportability.crawl_schedule()

    # TODO(kevin): Put the games in benchapp.
    print sportability.games

if __name__ == "__main__":
    main()
