import sys
import argparse

from . import detect_affiliate, strip_affiliate, add_affiliate

def detect(args):
    for url in args.urls:
        detect = detect_affiliate(url)

        if detect['affiliate_link']:
            print '[Affiliate] %s' % (url,)
        else:
            print '[NormalLnk] %s' % (url,)


def strip(args):
    for url in args.urls:
        stripped = strip_affiliate(url)
        print stripped

def add(args):
    for url in args.urls:
        new_url = add_affiliate(url, strip=args.strip)
        print new_url


parser = argparse.ArgumentParser(
    description='Detect, strip, and add affiliate links'
)

subparsers = parser.add_subparsers(
    title='Subcommands',
    description='Valid subcommands',
    help='additional help'
)

parser_detect = subparsers.add_parser('detect')
parser_detect.set_defaults(func=detect)
parser_detect.add_argument('urls', nargs='+')

parser_strip = subparsers.add_parser('strip')
parser_strip.set_defaults(func=strip)
parser_strip.add_argument('urls', nargs='+')

parser_add = subparsers.add_parser('add')
parser_add.add_argument('-s', '--strip', action='store_true')
parser_add.set_defaults(func=add)
parser_add.add_argument('urls', nargs='+')

args = parser.parse_args(sys.argv[1:])
args.func(args)

