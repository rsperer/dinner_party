# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import sys
import numpy as np

from permutate import get_perms

SEATING_FOR_GUESTS = 'Recommended seating for guests'

GUEST1_INDEX = 1
GUEST2_INDEX = 7
LIKENESS_INDEX = 11
SIGN_INDEX = 13
NUM_TOKENS = 14


class InputError(Exception):

    def __init__(self, message):
        self.message = message


def read_guests(filepath: str):
    guests_to_indices = {}
    indices_to_guests = {}
    with open(filepath) as fp:
        count = 0
        for line_num, line in enumerate(fp):
            tokens = line.strip().split(' ')
            if len(tokens) < NUM_TOKENS:
                raise InputError(f'Too few tokens in line #{line_num + 1}')
            guest1 = tokens[GUEST1_INDEX]
            guest2 = tokens[GUEST2_INDEX]
            count = add_to_guests(guests_to_indices, indices_to_guests, guest1, count)
            count = add_to_guests(guests_to_indices, indices_to_guests, guest2, count)
    return guests_to_indices, indices_to_guests


def read_preferences(filepath: str):
    guests_to_indices, indices_to_guests = read_guests(filepath)
    guest_count = len(guests_to_indices.keys())
    preferences = np.zeros((guest_count, guest_count))
    with open(filepath) as fp:
        for line_num, line in enumerate(fp):
            tokens = line.strip().split(' ')
            if len(tokens) < NUM_TOKENS:
                raise InputError(f'Too few tokens in line #{line_num + 1}')
            guest1 = tokens[GUEST1_INDEX]
            guest2 = tokens[GUEST2_INDEX]
            q = float(tokens[LIKENESS_INDEX])
            likeness = 100.0
            if tokens[SIGN_INDEX] == 'less':
                q *= -1
            likeness = (likeness + q) / 100.
            preferences[guests_to_indices[guest1], guests_to_indices[guest2]] = likeness
    return [preferences, indices_to_guests]


def triplet_score(left: int, center: int, right: int) -> float:
    return guest_preferences[center, left] * guest_preferences[center, right]


def calc_score(arrangement) -> float:
    num_guests = len(arrangement)
    score = 0.
    current_index = 0
    left_index = num_guests - 1
    right_index = 1
    while current_index < num_guests:
        score += scores[arrangement[left_index],
                        arrangement[current_index],
                        arrangement[right_index]]
        current_index += 1
        left_index = cyclic_inc(left_index, num_guests)
        right_index = cyclic_inc(right_index, num_guests)
    return score


def cyclic_inc(index, max_index) -> int:
    index += 1
    if index == max_index:
        index = 0
    return index


def add_to_guests(guest_list: dict, indices_list: dict, name: str, index: int) -> int:
    if name not in guest_list:
        guest_list[name] = index
        indices_list[index] = name
        return index+1
    return index


def find_best_seating(guest_list: []):
    all_perms = get_perms(guest_list)
    max_score = 0.
    best_p = []
    for p in all_perms:
        p_score = calc_score(p)
        if p_score > max_score:
            max_score = p_score
            best_p = p
    return best_p, max_score


def calc_scores(num):
    for i in range(num):
        for j in range(num):
            for k in range(num):
                if i == j or j == k or i == k or scores[i, j, k] != 1:
                    continue
                scores[i, j, k] = triplet_score(i, j, k)
                scores[k, j, i] = scores[i, j, k]


def print_seating(title: str, arrangement: [], score: float):
    print(f'{title}:\n {" ".join(guest_names[i] for i in arrangement)}. Happiness score: {score:.3f}')


if __name__ == '__main__':
    args = sys.argv
    if len(args) != 2:
        print('Usage: python optimal_seating.py <path to input text file>')
        exit(-1)

    try:
        guest_preferences, guest_names = read_preferences(args[1])
    except IOError:
        print(f'Error reading {args[1]}')
        exit(-1)
    except ValueError:
        print(f'Illegal happiness value at {args[1]}')
        exit(-1)
    except InputError as e:
        print(f'Error reading {args[1]}, {str(e)}')
        exit(-1)

    guest_number = len(guest_preferences)
    if guest_number <= 3:
        any_arrangement = range(guest_number)
        print_seating(SEATING_FOR_GUESTS, any_arrangement, calc_score(any_arrangement))
        exit(0)

    # calc scores in advance considering host as well
    scores = np.ones((guest_number+1, guest_number+1, guest_number+1))
    calc_scores(guest_number)

    # find best seating for guests
    orig_guest_list = range(guest_number)
    seating, seating_score = find_best_seating(orig_guest_list)
    print_seating(SEATING_FOR_GUESTS, seating, seating_score)

    # find my optimal place
    host_index = guest_number
    guest_names[host_index] = 'Hostess'
    best_score_with_host = 0
    best_arrangement_with_host = []
    for m in range(guest_number + 1):
        seating_with_host = seating[:m] + [host_index] + seating[m:]
        score_with_host = calc_score(seating_with_host)
        if score_with_host > best_score_with_host:
            best_score_with_host = score_with_host
            best_arrangement_with_host = seating_with_host
    print_seating('Seating with host', best_arrangement_with_host, best_score_with_host)

    # find best guest to move to children's table for original setting
    # turns out that with hostess at the table it is best to remove her
    best_perm = []
    best_score = 0
    guest_to_remove = -1
    for r in range(guest_number):
        modified_list = set(orig_guest_list)
        modified_list.remove(r)
        perm, local_score = find_best_seating(np.array(list(modified_list)))
        if local_score > best_score:
            best_score = local_score
            best_perm = perm
            guest_to_remove = r
    print_seating(f'When removing {guest_names[guest_to_remove]}', best_perm, best_score)

