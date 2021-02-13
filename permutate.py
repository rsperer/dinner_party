def get_perms(numbers):
    if len(numbers) == 1:
        return numbers.copy()
    result = []
    for i, v in enumerate(numbers):
        next_collection = []
        for k, u in enumerate(numbers):
            if k != i:
                next_collection.append(u)
        next_perms = get_perms(next_collection)
        if len(next_perms) == 1:
            result.append([v] + next_perms)
        else:
            for p in next_perms:
                result.append([v] + p)
    return result


