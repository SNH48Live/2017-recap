#!/usr/bin/env python3

import argparse
import base64
import collections
import io
import os
import re
import tempfile
import webbrowser

import jinja2
import matplotlib
matplotlib.rcParams.update({
    'backend': 'svg',
    'font.family': 'Songti SC',
    'svg.hashsalt': '',
})
import matplotlib.pyplot as plt
import numpy
from matplotlib.ticker import FixedFormatter, FixedLocator

from models import *


HERE = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.dirname(HERE)
TEMPLATES_DIR = os.path.join(ROOT, 'templates')
JINJA = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
)
JINJA.filters['b64encode'] = lambda s: base64.b64encode(s.encode('utf-8')).decode('utf-8')
JINJA.filters['count'] = lambda member, performances: sum(1 for p in performances if member in p)
JINJA.filters['decimal'] = lambda value: int(value) if int(value) == value else f'{value:.1f}'
JINJA.filters['next'] = lambda iterator: next(iterator, None)
JINJA.filters['splitlist'] = lambda l, chunksize, nchunks: [iter(l[i*chunksize:(i+1)*chunksize]) for i in range(nchunks)]
ATTENDANCE_TEMPLATE = JINJA.get_template('attendance.svg')
BREAKDOWN_TEMPLATE = JINJA.get_template('breakdown.svg')
CONVERTER_TEMPLATE = JINJA.get_template('converter.html')
PERFORMANCES_TEMPLATE = JINJA.get_template('performances.svg')
RANKING_TEMPLATE = JINJA.get_template('ranking.svg')
TIER_STATS_TEMPLATE = JINJA.get_template('tier-stats.svg')
SUMMARY_TEMPLATE = JINJA.get_template('summary.svg')

IMAGES_DIR = os.path.join(ROOT, 'images')
SVG_DIR = os.path.join(IMAGES_DIR, 'svg')
os.makedirs(SVG_DIR, exist_ok=True)

YEAR = 2017


def convert_svg_to_png():
    scale = 4
    items = []
    for filename in convert_svg_to_png.queue:
        with open(os.path.join(SVG_DIR, filename)) as fp:
            svg = fp.read()
        m = re.match(r'^<svg .* width="(?P<width>\d+)" height="(?P<height>\d+)">', svg)
        assert m
        width = int(m.group('width'))
        height = int(m.group('height'))
        png_filename = filename[:-4] + f'@{scale}x.png'
        items.append((svg, width, height, png_filename))

    fd, path = tempfile.mkstemp(suffix='.html')
    os.close(fd)
    with open(path, 'w') as fp:
        fp.write(CONVERTER_TEMPLATE.render(scale_factor=scale, items=items))
    webbrowser.open(path)

    convert_svg_to_png.queue.clear()

convert_svg_to_png.queue = []


def queue_svg_for_conversion(filename):
    assert filename.endswith('.svg')
    convert_svg_to_png.queue.append(filename)


def render(template, filename, **render_args):
    path = os.path.join(SVG_DIR, filename)
    content = template.render(**render_args)
    if os.path.exists(path):
        with open(path, 'r') as fp:
            existing_content = fp.read()
    else:
        existing_content = None
    if content != existing_content:
        with open(path, 'w') as fp:
            fp.write(content)
        print(path)
    if render.generate_png:
        queue_svg_for_conversion(filename)

render.generate_png = False

def plt_render(filename):
    path = os.path.join(SVG_DIR, filename)
    buf = io.BytesIO()
    plt.savefig(buf, bbox_inches='tight', format='svg')
    content = buf.getvalue()
    if os.path.exists(path):
        with open(path, 'rb') as fp:
            existing_content = fp.read()
    else:
        existing_content = None
    if content != existing_content:
        with open(path, 'wb') as fp:
            fp.write(content)
        print(path)
    buf.close()
    if render.generate_png:
        queue_svg_for_conversion(filename)

def generate_performance_list():
    render_args = dict(
        title=f'{YEAR}年度SNH48公演列表',
        performances=list(SNH48.performances),
        columns=2,
    )
    render(PERFORMANCES_TEMPLATE, 'performances.svg', **render_args)


# collection should support members, __contains__, and __str__ (used in title);
# e.g., SNH48, TeamS2, TeamN2, a MemberList with a custom __str__, etc.
# stats attributes (mean, median, percentile25, percentile75) will be directly
# set on collection, as well as the counts attribute which holds a sorted list
# of (member, count).
def generate_ranking(collection, filename):
    counts = {member: 0 for member in collection.members}
    for performance in SNH48.performances:
        for member in performance.performers:
            if member in counts:
                counts[member] += 1

    # Sort by counter first (decreasing), then member
    sortkey = lambda pair: (-pair[1], SNH48.index(pair[0]))
    counts = sorted(counts.items(), key=sortkey)
    collection.counts = counts
    rank = 0
    accumulated = 0
    current_count = 32767
    table_rows = []
    for member, count in counts:
        accumulated += 1
        if count < current_count:
            rank = accumulated
            current_count = count
        table_rows.append((member, count, rank))

    counts_np = numpy.array([count for member, count in counts])
    collection.mean = counts_np.mean()
    collection.median = numpy.median(counts_np)
    collection.percentile25 = numpy.percentile(counts_np, 75)
    collection.percentile75 = numpy.percentile(counts_np, 25)
    table_rows.append(('平均', collection.mean))
    table_rows.append(('中位', collection.median))
    table_rows.append(('25百分位', collection.percentile25))
    table_rows.append(('75百分位', collection.percentile75))

    render_args = dict(
        title=f'{YEAR}年度{collection}公演出勤排名表',
        entries=table_rows,
        columns=3,
    )
    render(RANKING_TEMPLATE, filename, **render_args)


# A hell lot of duplicate code from generate_ranking. I know.
def generate_tier_stats(tier_num):
    tier = SNH48.tiers[tier_num]
    election_ranks = dict(TIER_MEMBERS[tier_num])
    table_rows = []
    counts = {member: 0 for member in tier}
    for performance in SNH48.performances:
        for member in performance.performers:
            if member in counts:
                counts[member] += 1
    for member in tier:
        table_rows.append((member, election_ranks[member.name], counts[member]))

    counts_np = numpy.array([count for member, count in counts.items()])
    tier.mean = counts_np.mean()
    tier.median = numpy.median(counts_np)
    tier.percentile25 = numpy.percentile(counts_np, 75)
    tier.percentile75 = numpy.percentile(counts_np, 25)
    table_rows.append(('平均', tier.mean))
    table_rows.append(('中位', tier.median))
    table_rows.append(('25百分位', tier.percentile25))
    table_rows.append(('75百分位', tier.percentile75))

    tier_descriptions = {
        '3-1': '三选高飞组包括1至16名的成员。',
        '3-2': '三选梦想组包括17至32名的成员。',
        '3-3': '三选起飞组包括33至48名的成员。',
        '4-1': '四选星光组包括1至16名的成员。',
        '4-2': '四选高飞组包括17至32名的成员。',
        '4-3': '四选梦想组包括33至48名的成员。',
        '4-4': '四选奔跑组包括49至64名的成员。',
    }
    render_args = dict(
        title=f'{YEAR}年度{tier}公演出勤统计表',
        entries=table_rows,
        mean=tier.mean,
        columns=3,
        tier_description=tier_descriptions[tier_num],
    )
    render(TIER_STATS_TEMPLATE, f'tier{tier_num}-stats.svg', **render_args)


def generate_breakdown():
    # Each entry is a triplet (affiliation_identifier, print_name, total_performances)
    entries = []
    for team_id in TEAM_IDS:
        team = SNH48.teams[team_id]
        entries.append((team_id, str(team), len(team.performances)))

    rush_count = 0
    other_count = 0
    for performance in SNH48.performances:
        if performance.affiliation:
            continue
        if performance.stage == '我们向前冲':
            rush_count += 1
        else:
            other_count += 1
    entries.append(('joint', '向前冲', rush_count))
    entries.append(('joint', '其它', other_count))

    entries.append(('joint', '总计', len(SNH48.performances)))

    counts = [count for _, _, count in entries]
    assert sum(counts[:-1]) == counts[-1]

    render_args = dict(
        title=f'{YEAR}年度SNH48公演场次一览',
        entries=entries,
    )
    render(BREAKDOWN_TEMPLATE, 'breakdown.svg', **render_args)


def generate_summary():
    loop_vars = []
    divider = (None, None, None)
    loop_vars.append((SNH48, 'SNH48', 'snh48'))
    loop_vars.append(divider)
    for team_id in TEAM_IDS:
        team = SNH48.teams[team_id]
        loop_vars.append((team, str(team), team_id))
    loop_vars.append(divider)
    for gen_num in range(1, 9):
        generation = SNH48.generations[gen_num]
        loop_vars.append((generation, str(generation), f'gen{gen_num}'))
    loop_vars.append(divider)
    for tier_num in TIERS:
        tier = SNH48.tiers[tier_num]
        loop_vars.append((tier, str(tier), f'tier{tier_num}'))

    table_rows = []
    num_entries = 0
    num_dividers = 0
    for collection, name, identifier in loop_vars:
        if collection:
            table_rows.append((
                name,
                identifier,
                collection.mean,
                collection.median,
                collection.percentile25,
                collection.percentile75,
            ))
            num_entries += 1
        else:
            # None for a divider row
            table_rows.append(None)
            num_dividers += 1

    render_args = dict(
        title=f'{YEAR}年度SNH48公演出勤统计数据一览',
        rows=table_rows,
        num_entries=num_entries,
        num_dividers=num_dividers,
        references=table_rows[0][-4:],
    )
    render(SUMMARY_TEMPLATE, 'summary.svg', **render_args)


def generate_scatter():
    plt.figure(figsize=(8, 4))
    plt.title('2017年度SNH48各队成员公演出勤场次散点图')

    team_heights = [5, 4, 3, 2, 1]
    team_colors = ['#a2d5ed', '#be98c7', '#f8941d', '#b1d61b', '#03c070']
    dots_x = []
    dots_y = []
    dots_s = []  # areas
    dots_c = []  # colors
    base_area = numpy.pi * 4  # a circle of radius 2pt
    for team_id, height, color in zip(TEAM_IDS, team_heights, team_colors):
        team = SNH48.teams[team_id]
        counts = [count for member, count in team.counts]
        dedup = collections.Counter(counts)
        for count, occurrences in dedup.items():
            dots_x.append(count)
            dots_y.append(height)
            dots_s.append(base_area * occurrences)
            dots_c.append(color)
    plt.scatter(dots_x, dots_y, s=dots_s, c=dots_c, marker='o')

    # Draw lines at mean values.
    dots_x = []
    dots_y = []
    dots_s = []
    dots_c = []
    for team_id, height, color in zip(TEAM_IDS, team_heights, team_colors):
        team = SNH48.teams[team_id]
        dots_x.append(team.mean)
        dots_y.append(height)
        dots_s.append(500)
        dots_c.append(color)
    plt.scatter(dots_x, dots_y, s=dots_s, c=dots_c, marker='|', alpha=0.5)

    plt.xlim(xmin=0)
    plt.ylim((0, 6))
    plt.gca().yaxis.set_major_locator(FixedLocator(team_heights))
    # Roman numeral Ⅱ has ridiculous letter spacing when rendered in Songti SC.
    team_names = ['SII', 'NII', 'HII', 'X ', 'XII']
    plt.gca().yaxis.set_major_formatter(FixedFormatter(team_names))
    plt.text(0, -0.8, '注：每行的竖线代表该队成员公演场次的平均值。', fontsize='small')

    plt_render('scatter.svg')


def generate_attendance_tables():
    for team_id in TEAM_IDS:
        team = SNH48.teams[team_id]

        render_args = dict(
            title=f'{YEAR}年度{str(team)}常规公演出勤表',
            members=list(team.all),
            performances=list(team.performances),
            affiliation=team_id,
        )
        filename = f'{team_id}-regular.svg'
        render(ATTENDANCE_TEMPLATE, filename, **render_args)

        render_args = dict(
            title=f'{YEAR}年度{str(team)}联合公演出勤表',
            members=list(team.members),
            # Exclude 我们向前冲 from joint performances.
            performances=[performance for performance in SNH48.joint_performances
                          if performance.stage != '我们向前冲'],
            affiliation='joint',
            footnote='《我们向前冲》公演另行统计，不计入本表。',
        )
        filename = f'{team_id}-joint.svg'
        render(ATTENDANCE_TEMPLATE, filename, **render_args)

        # Calculate members of max attendance
        total = len(team.performances)
        counts = []
        for member in team.members:
            count = 0
            for performance in team.performances:
                if member in performance:
                    count += 1
            counts.append((member, count))
        counts.sort(key=lambda t: -t[1])
        max_count = counts[0][1]
        max_members = []
        for member, count in counts:
            if count != max_count:
                break
            max_members.append(member)
        print(f'{team} 最高出勤', end='')
        if max_count == total:
            print('（全勤）：', end='')
        else:
            print(f'（差{total - max_count}场）：', end='')
        print('、'.join(member.name for member in max_members))

    rush_performances = []
    rush_performers = MemberList()
    for performance in SNH48.joint_performances:
        if performance.stage == '我们向前冲':
            rush_performances.append(performance)
            for performer in performance.performers:
                rush_performers.add(performer)

    render_args = dict(
        title=f'{YEAR}年度我们向前冲公演出勤表',
        members=list(rush_performers),
        performances=rush_performances,
        affiliation='joint',
    )
    filename = 'rush.svg'
    render(ATTENDANCE_TEMPLATE, filename, **render_args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--png', action='store_true',
                        help='''generate PNG images in addition to SVG
                        (warning: this operation launches a fleet of brower
                        windows)''')
    args = parser.parse_args()
    render.generate_png = args.png

    generate_performance_list()
    generate_breakdown()
    generate_ranking(SNH48, 'global-ranking.svg')
    for team_id in TEAM_IDS:
        generate_ranking(SNH48.teams[team_id], f'{team_id}-ranking.svg')
    for generation in range(1, 9):
        generate_ranking(SNH48.generations[generation], f'gen{generation}-ranking.svg')
    for tier in TIERS:
        generate_tier_stats(tier)
    generate_summary()
    generate_scatter()
    generate_attendance_tables()

    if args.png:
        convert_svg_to_png()


if __name__ == '__main__':
    main()
