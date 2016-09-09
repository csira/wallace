from tests.utils.discover import scan_directory
from tests.utils.registry import get_running


def go(test_funcs):
    print

    total = 0
    for f in test_funcs:
        if total > 0 and total % 10 == 0:
            print

        total += 1

        try:
            f()
        except:
            print
            print f.__name__
            print
            raise

        print '.',

    print '\n'
    print total, 'succeeded'
    print


if __name__ == '__main__':
    scan_directory('.')
    go(get_running())
