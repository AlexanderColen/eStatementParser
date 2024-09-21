from eStatementParser2.parsers.scotiaParser import ScotiaParser


if __name__ == '__main__':
    # TODO: Parse command line arguments.
    directory = input('Please input the directory to parse from:\n>>> ')

    # TODO: Ask user for input to determine parser.
    p = ScotiaParser(directory=directory)
    p.read()
