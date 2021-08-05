from random import randrange


def new_task(pods):
    random_index = randrange(len(pods))
    task = pods[random_index]
    return task


def get_task_list(env, n):
    pods = env.get_pods()
    task_list = []
    for i in range(n):
        task_list.append(new_task(pods))
    return task_list
