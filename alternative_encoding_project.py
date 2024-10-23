#!/usr/bin/python3
# alc24 - 20 - project2 
# DO NOT remove or edit the lines above. Thank you.

import sys
from z3 import Optimize, sat, If, Bool, Sum, Int, Implies, And, Or # TODO: remove unnecessary imports

##### GLOBAL VARIABLES #####
solver = Optimize()
airport_to_city = {}            # key: airport, value: city
cities_to_visit = []            # list of tuples (airport, k_m, k_M)
flights = []                    # list of Flights (attributes: date, origin, destination, departure, arrival, cost)
flights_with_origin = {}        # key: airport, value: flights[]
flights_with_destination = {}   # key: airport, value: flights[]
##### end: GLOBAL VARIABLES #####


days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def date_to_string(d):
    month = 1
    while d > days_in_month[month - 1]:
        d -= days_in_month[month - 1]
        month += 1
    return f"{d:02}/{month:02}"

class Flight:
    def __init__(self, date, origin, destination, departure, arrival, cost, var):
        self.date = sum(days_in_month[:int(date[3:5]) - 1]) + int(date[0:2])
        self.origin = origin
        self.destination = destination
        self.departure = departure
        # self.arrival = arrival
        self.cost = int(cost)
        self.var = Bool(f"x_{int(var)}")
        self.var_name = f"x_{int(var)}"

    def __str__(self):
        return f"{date_to_string(self.date)} {airport_to_city[self.origin]} {airport_to_city[self.destination]} {self.departure} {self.cost}"
##### end: CLASSES #####



##### READ FROM STDIN #####
lines = sys.stdin.readlines()
n = int(lines[0])
##### end: READ FROM STDIN #####


##### HANDLE CITIES #####
city, airport = lines[1].split()
airport_to_city[airport] = city
flights_with_origin[airport] = []
flights_with_destination[airport] = []
base = airport

K_m = 0
for i in range(2, n+1):
    city, airport, k_m, k_M = lines[i].split()
    K_m += int(k_m)
    airport_to_city[airport] = city
    flights_with_origin[airport] = []
    flights_with_destination[airport] = []
    # cities_to_visit.append((airport, int(k_m), int(k_M)))
    cities_to_visit.append((airport, int(k_m), int(k_M)))
##### end: HANDLE CITIES #####


##### HANDLE FLIGHTS #####
m = int(lines[n+1])
flight_lines = [line.split() for line in lines[n+2: n+2 + m]]

for i in range(m):
    flight = Flight(*flight_lines[i], i+1)
    flights.append(flight)
    flights_with_origin[flight.origin].append(flight)
    flights_with_destination[flight.destination].append(flight)

solver.minimize(Sum([If(flight.var, flight.cost, 0) for flight in flights]))
##### end: HANDLE FLIGHTS #####


##### CONSTRAINTS #####
first_date = flights[0].date
last_date = flights[-1].date
K = last_date - first_date

a_c = {}
d_c = {}
for city in airport_to_city:
    a_c[city] = Int(f"a_{city}")
    d_c[city] = Int(f"d_{city}")
    solver.add(And(a_c[city] >= first_date, a_c[city] <= last_date))
    solver.add(And(d_c[city] >= first_date, d_c[city] <= last_date))
    solver.add(Sum([flight.var for flight in flights_with_destination[city]]) == 1)
    solver.add(Sum([flight.var for flight in flights_with_origin[city]]) == 1)

for flight in flights:
    solver.add(Implies(flight.var, And(a_c[flight.destination] == flight.date, d_c[flight.origin] == flight.date)))

for city, k_m, k_M in cities_to_visit:
    solver.add(k_m <= d_c[city] - a_c[city])
    solver.add(d_c[city] - a_c[city] <= k_M)

for city1, _, _ in cities_to_visit:
    for city2, _, _ in cities_to_visit:
        if city1 != city2:
            solver.add(Or(d_c[city1] <= a_c[city2], d_c[city2] <= a_c[city1]))

solver.add(Sum([If(d_c[base] == a_c[city], 1, 0) for city, _, _ in cities_to_visit]) == 1)
solver.add(Sum([If(a_c[base] == d_c[city], 1, 0) for city, _, _ in cities_to_visit]) == 1)
##### end: CONSTRAINTS #####


##### SOLVING #####
if solver.check() == sat:
    model = solver.model()
    selected_vars = [str(var) for var in model if model[var] == True]
    selected_flights = [f for f in flights if f.var_name in selected_vars]
    total_cost = sum(f.cost for f in selected_flights)

    print(total_cost)
    for f in selected_flights:
        print(f)
##### end: SOLVING #####
