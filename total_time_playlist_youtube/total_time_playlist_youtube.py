#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


# TODO: возможно, если роликов будет слишком много, не все вернутся из запроса
def count_total_playlist_time(url, proxy=None, proxy_type='http'):
    """Функция парсит страницу плейлиста и подсчитывает сумму продолжительности роликов."""

    import grab
    g = grab.Grab()
    if proxy:
        g.setup(proxy=proxy, proxy_type=proxy_type)

    g.go(url)

    video_list = g.doc.select('//*[@class="pl-video yt-uix-tile "]')
    time_list = g.doc.select('//*[@class="timestamp"]')

    total_seconds = 0

    print('Playlist:')
    for i, (video, time) in enumerate(zip(video_list, time_list), 1):
        time_str = time.text()
        print('{}. {} ({})'.format(i, video.attr('data-title'), time_str))

        time_split = time_str.split(':')
        if len(time_split) == 3:
            h, m, s = map(int, time_split)
            total_seconds += h * 60 * 60 + m * 60 + s
        elif len(time_split) == 2:
            m, s = map(int, time_split)
            total_seconds += m * 60 + s
        else:
            total_seconds += int(time_split[0])

    return total_seconds


if __name__ == '__main__':
    url = 'https://www.youtube.com/playlist?list=PLqf5JRBicHXnV4fUNPJtE2YFAjPMHRX4K'
    # url = 'https://www.youtube.com/playlist?list=PLKom48yw6lJpyYN2Q_zmss68ntjzxxpHd'
    url = 'https://www.youtube.com/playlist?list=PLvX4-HTvsLu-j-K9n14cV5OvxwBl_8Won'

    import config
    total_seconds = count_total_playlist_time(url, config.proxy, config.proxy_type)

    from datetime import timedelta
    print('\nTotal time: {} ({} total seconds).'.format(timedelta(seconds=total_seconds), total_seconds))
