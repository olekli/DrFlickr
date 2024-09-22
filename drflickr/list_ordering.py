# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0


def getOutOfOrderIndices(sequence):
    if len(sequence) <= 1:
        return []
    n = len(sequence)
    lds = [1] * n
    predecessors = [-1] * n

    for i in range(1, n):
        for j in range(i):
            if sequence[j] > sequence[i] and lds[j] + 1 > lds[i]:
                lds[i] = lds[j] + 1
                predecessors[i] = j

    max_length = max(lds)
    index = lds.index(max_length)

    lds_sequence_indices = []
    while index != -1:
        lds_sequence_indices.append(index)
        index = predecessors[index]

    return [
        index for index, _ in enumerate(sequence) if index not in lds_sequence_indices
    ]


def orderPhotos(photos, window_begin, window_end):
    assert window_begin > window_end
    for photo in photos:
        assert window_begin > photo['date_posted']
        assert window_end < photo['date_posted']
    needs_move = getOutOfOrderIndices([photo['date_posted'] for photo in photos])
    needs_move = [i + 1 for i in needs_move]

    photos.insert(0, {'date_posted': window_begin})
    photos.insert(len(photos), {'date_posted': window_end})

    for index, photo in ((i, p) for i, p in enumerate(photos) if i in needs_move):
        next_index = index
        while next_index in needs_move:
            next_index += 1
        assert next_index != index

        new_time = (
            photos[index - 1]['date_posted'] + photos[next_index]['date_posted']
        ) / 2
        photo['date_posted'] = int(new_time)
        photo['date_taken'] = int(new_time)

    needs_move = getOutOfOrderIndices([photo['date_posted'] for photo in photos])
    assert len(needs_move) == 0
