import argparse
from src.trader import activate, activate_offline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--offline", help="running the agent offline. reads from DB instead of API",
                        action="store_true")
    args = parser.parse_args()

    if args.offline:
        activate_offline()
    else:
        activate()


if __name__ == '__main__':
    main()
