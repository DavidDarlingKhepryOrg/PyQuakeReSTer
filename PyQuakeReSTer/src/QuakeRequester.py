# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 16:02:09 2017

@author: Khepry Quixote
"""
import argparse
import requests
import sys


from datetime import datetime, timedelta
from monthdelta import monthdelta
from pprint import pprint
from time import sleep

# handle incoming parameters,
# pushing their values into the
# args dictionary for later usage

arg_parser = argparse.ArgumentParser(description='Obtain earthquakes via ReSTful interface')

arg_parser.add_argument('--bgn_date',
                        type=str,
                        default='1900-01-01',
                        help='starting date')
arg_parser.add_argument('--end_date',
                        type=str,
                        default='2016-01-01',
                        help='ending date')
arg_parser.add_argument('--iteration_type',
                        type=str,
                        default='years',
                        choices=('days','weeks','months', 'years'),
                        help='iteration type (e.g. days, weeks, months, years)')
arg_parser.add_argument('--how_many_iterations',
                        type=int,
                        default=3,
                        help='how many iterations')

arg_parser.add_argument('--method',
                        type=str,
                        default='query',
                        choices=('count','query'),
                        help='method to use')
arg_parser.add_argument('--format',
                        type=str,
                        default='csv',
                        choices=('csv','geojson','kml', 'quakeml', 'text', 'xml'),
                        help='format of output')
arg_parser.add_argument('--min_magnitude',
                        type=float,
                        help='minimum magnitude (0 or greater)')
arg_parser.add_argument('--max_magnitude',
                        type=float,
                        help='maximum magnitude (0 or greater)')
arg_parser.add_argument('--min_depth',
                        type=float,
                        default=-100,
                        help='minimum depth in kilometers (-100 to 1000)')
arg_parser.add_argument('--max_depth',
                        type=float,
                        default=1000,
                        help='maximum depth in kilometers (-100 to 1000)')
arg_parser.add_argument('--sleep_seconds',
                        type=int,
                        default=5,
                        help='sleep seconds')

args = arg_parser.parse_args()

def get_next_dates_list(bgn_date,
                        end_date,
                        iteration_type,
                        how_many_iterations):
    bgn_end_dates = []
    date_time = bgn_date
    for _i in range(0, how_many_iterations):
        bgn_date = date_time.strftime('%Y-%m-%d')
        try:
            if iteration_type == 'days':
                date_time += timedelta(days=1)
                max_date = (date_time + timedelta(days=1)).strftime('%Y-%m-%d')
            elif iteration_type == 'weeks':
                date_time += timedelta(weeks=1)
                max_date = date_time.strftime('%Y-%m-%d')
            elif iteration_type == 'months':
                date_time += monthdelta(months=1)
                max_date = date_time.strftime('%Y-%m-%d')
            elif iteration_type == 'years':
                date_time += monthdelta(months=12)
                max_date = date_time.strftime('%Y-%m-%d')
            else:
                date_time += timedelta(days=1)
                max_date = (date_time + timedelta(days=1)).strftime('%Y-%m-%d')
            if datetime.strptime(max_date, '%Y-%m-%d') < end_date:
                bgn_end_dates.append((bgn_date, max_date))
            else:
                bgn_end_dates.append((bgn_date, end_date.strftime('%Y-%m-%d')))
                break
        except Exception as e:
            sys.stderr.write('Exception: %s' % e)
    return bgn_end_dates

first_pass = True    

base_url = 'https://earthquake.usgs.gov/fdsnws/event/1/'
base_url += 'count?' if args.method == 'count' else 'query?'
base_url += 'format=%s' % args.format
base_url += '&mindepth=%d' % args.min_depth
base_url += '&maxdepth=%d' % args.max_depth
base_url += '&minmagnitude=%d' % args.min_magnitude if args.min_magnitude is not None else ''
base_url += '&maxmagnitude=%d' % args.max_magnitude if args.max_magnitude is not None else ''

bgn_date = datetime.strptime(args.bgn_date, '%Y-%m-%d')
end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
bgn_end_dates = get_next_dates_list(bgn_date,
                                    end_date,
                                    args.iteration_type,
                                    args.how_many_iterations)
for bgn_end_date in bgn_end_dates:
    url = '%s&starttime=%s&endtime=%s' % (base_url, bgn_end_date[0], bgn_end_date[1])
    # print(url)
    try:
        response = requests.get(url)
        content = response.content
        content_decoded = content.decode('utf-8')
        if first_pass:
            print(content_decoded.strip())
            first_pass = False
        else:
            print(content_decoded[content_decoded.find('\n')+1:].strip())
    except Exception as e:
        print('Bad response. Got an error code:', e)
    sleep(args.sleep_seconds)
    
print('Processing finished!')
