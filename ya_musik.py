from yandex_music import Client

import pygame


client = Client('AQAAAABPjoOCAAG8XpOZD-Z8fUKUiF9kC6YiBYM').init()
count = 0
def play():
    pygame.init()
    client.users_likes_tracks()[count].fetch_track().download('downloads/music/example.mp3')

    song = pygame.mixer.Sound('downloads/music/example.mp3')
    clock = pygame.time.Clock()
    song.play()
    while True:
        clock.tick(60)
pygame.quit()

def skip():
    pygame.init()
    global count
    count += 1
    client.users_likes_tracks()[count].fetch_track().download('downloads/music/example.mp3')

    pygame.mixer.stop()
    return play()
def stop():
    global count
    count = 0
    pygame.mixer.stop()
type_to_name = {
    'track': 'трек',
    'artist': 'исполнитель',
    'album': 'альбом',
    'playlist': 'плейлист',
    'video': 'видео',
    'user': 'пользователь',
    'podcast': 'подкаст',
    'podcast_episode': 'эпизод подкаста',
}


def send_search_request_and_print_result(query):
    search_result = client.search(query)

    text = [f'Результаты по запросу "{query}":', '']

    best_result_text = ''
    if search_result.best:
        type_ = search_result.best.type
        best = search_result.best.result

        text.append(f'❗️Лучший результат: {type_to_name.get(type_)}')

        if type_ in ['track', 'podcast_episode']:
            artists = ''
            if best.artists:
                artists = ' - ' + ', '.join(artist.name for artist in best.artists)
            best_result_text = best.title + artists
        elif type_ == 'artist':
            best_result_text = best.name
        elif type_ in ['album', 'podcast']:
            best_result_text = best.title
        elif type_ == 'playlist':
            best_result_text = best.title
        elif type_ == 'video':
            best_result_text = f'{best.title} {best.text}'

        text.append(f'Содержимое лучшего результата: {best_result_text}\n')

    if search_result.artists:
        text.append(f'Исполнителей: {search_result.artists.total}')
    if search_result.albums:
        text.append(f'Альбомов: {search_result.albums.total}')
    if search_result.tracks:
        text.append(f'Треков: {search_result.tracks.total}')
    if search_result.playlists:
        text.append(f'Плейлистов: {search_result.playlists.total}')
    if search_result.videos:
        text.append(f'Видео: {search_result.videos.total}')

    text.append('')
    print('\n'.join(text))


if __name__ == '__main__':
    while True:
        input_query = input('Введите поисковой запрос: ')
        send_search_request_and_print_result(input_query)