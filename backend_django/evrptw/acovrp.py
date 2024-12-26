import numpy as np
import random
import pandas as pd
from tqdm import tqdm
import time

def acovrp(num_ants, alpha, beta, rho, num_iterations, distance_matrix, spendtm_matrix, vehicle_capacity, customer_demands, time_windows, service_time, time_limit, quit):
    # Number of customers (not including the depot)
    num_customers = len(customer_demands)

    Q = 100      # Pheromone intensity

    global pheromone_matrix
    pheromone_matrix = pd.DataFrame(1, index=distance_matrix.index, columns=distance_matrix.columns)

    # Run the ACO algorithm
    best_solution = None
    best_cost = float('inf')
    cost_iteration = []
    improvement = []
    improved = []
    iteration_time = []
    converged = False
    finished = False
    total_start_time = time.time()
    for iteration in range(num_iterations):
        if time.time() - total_start_time > time_limit:
            print("Time limit exceeded. Quit.")
            break
        print(f"Iteration: {iteration}, Best Cost: {best_cost}")
        start_time = time.time()
        solutions = []
        if converged and quit:
            print("No more significant improvement. Quit.")
            break
        for i in range(num_ants):
            solution, finished = construct_solution(num_customers, distance_matrix, customer_demands, spendtm_matrix, 
                                        time_windows, vehicle_capacity, service_time, alpha, beta)
            solutions.append(solution)

        update_pheromones(solutions, distance_matrix, spendtm_matrix, customer_demands, time_windows, service_time, rho, Q)
        # Find the best solution in this iteration
        for solution in solutions:
            if all(check_time_window_feasibility(route, spendtm_matrix, time_windows, service_time) for route in solution) and \
                all(check_driving_range_feasibility(route, distance_matrix) for route in solution):
                cost = sum(calculate_route_cost(route, distance_matrix, spendtm_matrix, 
                                                customer_demands, time_windows)[1] for route in solution)
                if cost < best_cost:
                    improvement.append(best_cost - cost)
                    improved.append(iteration)
                    best_solution = solution
                    best_cost = cost
                    print(f"Iteration: {iteration} Current best cost: {best_cost}")
                    if len(improved) < 2:
                        continue
                    if improved[len(improved)-1]-improved[len(improved)-2] > improved[len(improved)-2]:
                        if improvement[len(improvement)-1]-improvement[len(improvement)-2] < 0.05*improvement[len(improvement)-2]:
                            converged = True
        cost_iteration.append(best_cost)
        end_time = time.time()
        iteration_time.append(end_time - start_time)

    if best_solution is None or not finished:
        print("No feasible solution found.")
        best_cost = float('inf')
        best_solution = None
        cost_iteration = None
        iteration_time = None
    else:
        print("\nBest solution found:")
        for route in best_solution:
            vehicle, route_cost = calculate_route_cost(route, distance_matrix, spendtm_matrix,
                                                    customer_demands, time_windows)
            print(f"Vehicle: {vehicle}, Route: {[int(i) for i in route]}, Cost: {route_cost}")
        print(f"Total cost: {best_cost}")

    return best_cost, best_solution, cost_iteration, iteration_time

def calculate_route_cost(route, distance_matrix, spendtm_matrix, customer_demands, time_windows):
    total_weight = 0
    total_volume = 0
    trans_distance = 0
    max_distance = 0
    current_distance = 0
    charging_cost = 0
    for i in range(len(route) - 1):
        if route[i] > 1000:
            if current_distance > max_distance:
                max_distance = current_distance
            current_distance = 0
        else:
            current_distance += distance_matrix[route[i]][route[i + 1]]
        trans_distance += distance_matrix[route[i]][route[i + 1]]
        if route[i] > 1000:
            charging_cost += 50
    for id, (weight, volume) in customer_demands.items():
        if id in route:
            total_volume += volume
            total_weight += weight
    if total_volume <= 12 and total_weight <= 2 and max_distance <= 100000:
        vehicle_type = 1
        vehicle_cost = 200
        unit_cost = 12
    else:
        vehicle_type = 2
        vehicle_cost = 300
        unit_cost = 14
    trans_cost = 0
    trans_cost = (trans_distance / 1000) * unit_cost
    waiting_time = calculate_waiting_time(route, spendtm_matrix, time_windows, 30)
    waiting_cost = waiting_time * 0.4
    cost = vehicle_cost + charging_cost + trans_cost + waiting_cost
    return vehicle_type, cost

def check_time_window_feasibility(route, spendtm_matrix, time_windows, service_time):
    if time_windows[route[1]][0] > spendtm_matrix[route[0]][route[1]]:
        current_time = time_windows[route[1]][0] - spendtm_matrix[route[0]][route[1]]
    else:
        current_time = 0
    for i in range(len(route) - 1):
        travel_time = spendtm_matrix[route[i]][route[i + 1]]
        current_time += travel_time

        next_customer = route[i + 1]
        arrival_time = current_time
        if next_customer == 0:
            if arrival_time > 960:
                return False
        elif next_customer <= 1000:
            if arrival_time < time_windows[next_customer][0]:
                arrival_time = time_windows[next_customer][0]
            if arrival_time > time_windows[next_customer][1]:
                return False
            current_time = arrival_time + service_time
    return True

def check_driving_range_feasibility(route, distance_matrix):
    current_distance = 0
    for i in range(len(route) - 1):
        if route[i] > 1000:
            current_distance = 0
        else:
            travel_distance = distance_matrix[route[i]][route[i + 1]]
            current_distance += travel_distance
            
        if current_distance > 120000:
            return False
    return True

def construct_solution(num_customers, distance_matrix, customer_demands, spendtm_matrix, time_windows, 
                    vehicle_capacity, service_time, alpha, beta):
    solution = []
    visited = set()
    workable = True
    finished = False
    
    while len(visited) < num_customers:
        current_route = [0]  # Start at depot
        current_load = [0, 0]
        current_time = 0  # Start at time 0
        current_distance = 0

        while workable:
            next_customer, is_charger = choose_next_customer(current_route[-1], visited, current_load, 
                                        current_time, current_distance, customer_demands, vehicle_capacity,
                                        spendtm_matrix, time_windows, distance_matrix, alpha, beta)
            if next_customer is None:
                if current_route[-1] == 0:
                    workable = False
                break  # Return to depot when no more feasible customers
            if not is_charger:
                visited.add(next_customer)
                current_load[0] += customer_demands[next_customer][0]
                current_load[1] += customer_demands[next_customer][1]
            current_route.append(next_customer)
            current_time += spendtm_matrix[current_route[-2]][current_route[-1]]
            if is_charger:
                current_distance = 0
            else:
                current_distance += distance_matrix[current_route[-2]][current_route[-1]]
                if current_time < time_windows[current_route[-1]][0]:
                    current_time = time_windows[current_route[-1]][0]
            current_time += service_time

        if not workable:
            break
        solution.append(current_route + [0])  # Return to depot for final route

    if len(visited) == num_customers:
        finished = True
    return solution, finished

def choose_next_customer(current_customer, visited, current_load, current_time, 
                        current_distance, customer_demands, vehicle_capacity, spendtm_matrix,
                        time_windows, distance_matrix, alpha, beta):
    if current_time > 930:
        return (None, False)
    if random.random() < current_distance/120000 and current_customer <= 1000:
        nodes_list = spendtm_matrix.index.tolist()
        charger_list = [x for x in nodes_list if x > 1000]
        is_charger = True
        feasible_customers = [
            i for i in charger_list
            if current_distance + distance_matrix[current_customer][i] <= 120000]
    else:
        is_charger = False
        unvisited_customer_demands = [
            customer for customer in customer_demands if customer not in visited
        ]
        feasible_customers = [
            i for i in unvisited_customer_demands
            if current_load[0] + customer_demands[i][0] <= vehicle_capacity[0] and
            current_load[1] + customer_demands[i][1] <= vehicle_capacity[1] and
            current_time + spendtm_matrix[current_customer][i] <= time_windows[i][1]
        ]
    if not feasible_customers:
        return (None, False)
    
    # Calculate the probabilities for choosing the next customer
    pheromones = np.array([pheromone_matrix[current_customer][j] for j in feasible_customers])
    distances = np.array([distance_matrix[current_customer][j] for j in feasible_customers])
    epsilon = 1e-10
    probabilities = (pheromones ** alpha) * ((1 / (distances + epsilon)) ** beta)
    probabilities_sum = probabilities.sum()

    if probabilities_sum > 0:
        probabilities /= probabilities_sum
    else:
        return (None, False)
    
    choice = np.random.choice(feasible_customers, p=probabilities)
    return (choice, is_charger)

def calculate_waiting_time(route, spendtm_matrix, time_windows, service_time):
    current_time = 0  # Start at time 0 (can be adjusted)
    waiting_time = 0
    for i in range(len(route) - 1):
        travel_time = spendtm_matrix[route[i]][route[i + 1]]
        current_time += travel_time
        
        next_customer = route[i + 1]
        arrival_time = current_time
        if next_customer == 0:
            if arrival_time > 960:
                return waiting_time
        elif next_customer > 1000:
            current_time = arrival_time + service_time
        else:
            if arrival_time < time_windows[next_customer][0]:
                arrival_time = time_windows[next_customer][0]
                waiting_time += time_windows[next_customer][0] - arrival_time
            current_time = arrival_time + service_time
    return waiting_time

def update_pheromones(solutions, distance_matrix, spendtm_matrix, customer_demands, time_windows, service_time, rho, Q):
    global pheromone_matrix
    pheromone_matrix *= (1 - rho)  # Evaporation
    for solution in solutions:
        if all(check_time_window_feasibility(route, spendtm_matrix, time_windows, service_time) for route in solution):
            cost = sum(calculate_route_cost(route, distance_matrix, spendtm_matrix, 
                                            customer_demands, time_windows)[1] for route in solution)
            for route in solution:
                for i in range(len(route) - 1):
                    pheromone_matrix.loc[route[i], route[i + 1]] += Q / cost
