import numpy as np
import copy


def print_timetable(timetable, groups):
    days = len(timetable[groups[0]])

    for day in range(days):
        print(f"Day {day + 1}:\n")
        for subject_number in range(max_subjects_per_day):
            subjects_info = [
                f"{group}: {timetable[group][day][subject_number][0]} ({timetable[group][day][subject_number][1]})" for
                group in groups]
            print(f"  Subject {subject_number + 1}: {', '.join(subjects_info)}")
        print("\n" + "-" * 40 + "\n")


def initialize_population(size, subjects, subjects_constraint, group_constraint, days, max_subjects):
    population = []
    for i in range(size):
        individual = {}
        for group in group_constraint.keys():
            individual[group] = []
            for day in range(days):
                day_timetable = []
                for subject_number in range(max_subjects):
                    subject = np.random.choice(subjects, 1)[0]
                    teacher = '' if subject == '' else np.random.choice(subjects_constraint[subject], 1)[0]
                    day_timetable.append((subject, teacher))
                individual[group].append(day_timetable)
        population.append(individual)
    return population


def fitness_function(individual, days, max_subjects):
    total_penalty = 0
    individual_group_constraint = copy.deepcopy(group_constraint)
    individual_teacher_constraint = copy.deepcopy(teacher_constraint)
    teachers_multiple_groups_constraint = {teacher: timetable for teacher, timetable in
                                           zip(individual_teacher_constraint.keys(),
                                               [[[False for j in range(max_subjects)] for i in range(days)] for teacher
                                                in range(len(individual_teacher_constraint.keys()))])}

    for group in individual.keys():
        for day in range(days):
            for subject_number in range(max_subjects):
                subject, teacher = individual[group][day][subject_number]
                if subject != '':
                    if teachers_multiple_groups_constraint[teacher][day][subject_number]:
                        total_penalty += 10
                    teachers_multiple_groups_constraint[teacher][day][subject_number] = True
                    individual_group_constraint[group][subject] -= 1
                    individual_teacher_constraint[teacher] -= 1

    for hours in map(lambda values: values.values(), individual_group_constraint.values()):
        for hour in hours:
            if (hour != 0):
                total_penalty += np.abs(hour)

    for hours in individual_teacher_constraint.values():
        if (hour < 0):
            total_penalty += np.abs(hour)

    return 1 / (1 + total_penalty)


def crossover(parent1, parent2):
    child = {}
    for group in parent1.keys():
        child[group] = []
        for day in range(len(parent1[group])):
            crossover_point = np.random.randint(0, len(parent1[group][day]))
            child[group].append(parent1[group][day][:crossover_point] + parent2[group][day][crossover_point:])

    return child


def mutate(individual, subjects, subject_constraint, days, max_subjects):
    mutated_individual = individual.copy()

    group = np.random.choice(list(individual.keys()), 1)[0]

    day = np.random.randint(0, days)
    subject_number = np.random.randint(0, max_subjects)

    mutation = np.random.choice(subjects, 1)[0]
    mutated_individual[group][day][subject_number] = (
    mutation, np.random.choice(subject_constraint[mutation], 1)[0]) if mutation != '' else ('', '')

    return mutated_individual


def genetic_algorithm(population_size, generations, mutation_rate, crossover_level, subjects, subjects_constraint, group_constraint,
                      teachers_constraint, days, max_subjects):
    population = initialize_population(population_size, subjects, subjects_constraint, group_constraint, days,
                                       max_subjects)

    for generation in range(generations):
        fitness_scores = [fitness_function(individual, days, max_subjects) for individual in population]

        selected_parents = np.random.choice(population, size=population_size * 2 // 3,
                                            p=fitness_scores / np.sum(fitness_scores), replace=True)

        offspring = []
        for i in range(0, len(selected_parents) - 1, 2):
            parent1 = selected_parents[i]
            parent2 = selected_parents[i + 1]
            if np.random.rand() < crossover_level:
                child = crossover(parent1, parent2)
            else:
                child = parent1
            offspring.append(child)

        for i in range(len(offspring)):
            if np.random.rand() < mutation_rate:
                offspring[i] = mutate(offspring[i], subjects, subjects_constraint, days, max_subjects)

        population = selected_parents.tolist() + offspring
        if (generation) % 100 == 0:
            print(f"Generation {generation} - Best Fitness: {max(fitness_scores)}")

        if(max(fitness_scores) == 1):
            print(f"Schedule found on {generation} iteration.")
            break
    return population



pop_size = 50
gen_count = 1000
mut_rate = 0.3
cross_level = 0.8
days = 5
max_subjects_per_day = 5

subjects = ['linalg', 'calculus', 'db', 'english', 'stats', 'ai', '']
groups = ['tk', 'mi', 'ttp']

subjects_constraint = {
    'linalg': ['teacher1', 'teacher2'],
    'calculus': ['teacher1', 'teacher3'],
    'db': ['teacher3'],
    'english': ['teacher6'],
    'stats': ['teacher4', 'teacher5'],
    'ai': ['teacher4', 'teacher5']
}

group_constraint = {
    'tk': {'linalg': 5, 'calculus': 2, 'db': 5, 'english': 2, 'stats': 2, 'ai': 3},
    'mi': {'linalg': 5, 'calculus': 5, 'db': 5, 'english': 1, 'stats': 5, 'ai': 1},
    'ttp': {'linalg': 5, 'calculus': 3, 'db': 5, 'english': 2, 'stats': 2, 'ai': 1}
}

teacher_constraint = {
    'teacher1': 13,
    'teacher2': 8,
    'teacher3': 15,
    'teacher4': 7,
    'teacher5': 7,
    'teacher6': 5
}

solutions = genetic_algorithm(pop_size, gen_count, mut_rate, cross_level, subjects, subjects_constraint, group_constraint,
                              teacher_constraint, days, max_subjects_per_day)

res = sorted(solutions, key=lambda x: fitness_function(x, days, max_subjects_per_day), reverse=True)[:10]



print("Solution - Fitness:", fitness_function(res[0], days, max_subjects_per_day), '\n')
print_timetable(res[0], groups)
