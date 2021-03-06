import argparse
import requests
import sys

from benchapp import BenchApp
from game import Game
from sportability import Sportability

def main():
    # Parse command line args.
    parser = argparse.ArgumentParser(description='Sync Benchapp schedule with '
                                     'Sportability.')
    parser.add_argument('-l', '--sa_leagueid',
                        help='Sportability league id',
                        required=True)
    parser.add_argument('-t', '--sa_teamid',
                        help='Sportability team id',
                        required=True)
    parser.add_argument('-n', '--teamname',
                        help='Team name',
                        required=True)
    parser.add_argument('-e', '--ba_email',
                        help='Benchapp e-mail address',
                        required=True)
    parser.add_argument('-p', '--ba_password',
                        help='Benchapp password',
                        required=True)
    parser.add_argument('-d', '--mg_domain',
                        help='Mailgun domain')
    parser.add_argument('-k', '--mg_key',
                        help='Mailgun secret key')
    parser.add_argument('-r', '--dry_run',
                        action='store_true',
                        default=False,
                        help='Dry run')
    args = parser.parse_args()

    print 'Crawling Schedules...'

    # Crawl Sportability.
    sportability = Sportability(args.sa_leagueid,
                                args.sa_teamid,
                                args.teamname)
    sportability.crawl_schedule()

    # Crawl Benchapp.
    benchapp = BenchApp(args.ba_email, args.ba_password, args.teamname)
    benchapp.crawl_schedule()

    # Debugging
    # print 'sportability: ' + str(sportability.games) + '\nbenchapp' + str(benchapp.games)

    # Find games to add to and remove from Benchapp.
    added_games, removed_games = Game.diff(benchapp.games, sportability.games)
    print 'Adding %d games, Removing %d games...' % (len(added_games),
                                                     len(removed_games))

    # Quit if dry run.
    if args.dry_run:
        return

    # E-mail updates.
    if (len(added_games) or len(removed_games)) and args.mg_domain and args.mg_key:
        requests.post("https://api.mailgun.net/v3/%s/messages" % args.mg_domain,
                      auth=("api", args.mg_key),
                      data={"from": "benchappsync <mailgun@%s>" % args.mg_domain,
                            "to": [args.ba_email],
                            "subject": "%s Schedule Updated" % args.teamname,
                            "text": "Adding %d games, Removing %d games..." % (len(added_games), len(removed_games))})

    benchapp.add_games(added_games)
    benchapp.remove_games(removed_games)

    print 'Sync Completed Succesfully'

if __name__ == "__main__":
    main()
