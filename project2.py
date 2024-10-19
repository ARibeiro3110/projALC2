#!/usr/bin/python3
# alc24 - 20 - project2 
# DO NOT remove or edit the lines above. Thank you.

import sys
from z3 import Optimize, sat, If, Bool, Sum

##### GLOBAL VARIABLES #####
solver = Optimize()
airport_to_city = {}            # key: airport, value: city
cities_to_visit = []            # list of tuples (airport, k_m, k_M)
flights = []                    # list of Flights (attributes: date, origin, destination, departure, arrival, cost)
flights_with_origin = {}        # key: airport, value: flights[]
flights_with_destination = {}   # key: airport, value: flights[]
##### end: GLOBAL VARIABLES #####


##### CLASSES #####
class Date:
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    def __init__(self, day, month):
        self.day = int(day)
        self.month = int(month)
        self.ordinal = sum(self.days_in_month[:self.month - 1]) + self.day

    def __str__(self):
        return f"{self.day:02}/{self.month:02}"

    def nightsBetween(self, dt):
        return dt.ordinal - self.ordinal

class Flight:
    def __init__(self, date, origin, destination, departure, arrival, cost, var):
        self.date = Date(date[0:2], date[3:5])
        self.origin = origin
        self.destination = destination
        self.departure = departure
        # self.arrival = arrival
        self.cost = int(cost)
        self.var = Bool(f"x_{int(var)}")
        self.var_name = f"x_{int(var)}"
        # solver.add(And(0 <= self.var, self.var <= 1))

    def __str__(self):
        return f"{self.date} {airport_to_city[self.origin]} {airport_to_city[self.destination]} {self.departure} {self.cost}"
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

K = flights[0].date.nightsBetween(flights[-1].date) # TODO: needed?
##### end: HANDLE FLIGHTS #####


##### FOR EACH CITY, ARRIVAL AND DEPARTURE ARE k_m to k_M NIGHTS APART #####
for airport, k_m, k_M in cities_to_visit + [(base, K_m, K)]:
    if airport != base:
        arrivals = flights_with_destination[airport]
        departures = flights_with_origin[airport]
    else:
        arrivals = flights_with_origin[airport]
        departures = flights_with_destination[airport]

    arrival_vars = [f.var for f in arrivals]
    solver.add(Sum([If(var, 1, 0) for var in arrival_vars]) == 1)

    # departure_vars = [f.var for f in departures]
    # solver.add(Sum([If(var, 1, 0) for var in departure_vars]) == 1)

    for f_arrival in arrivals:
        compatible_departures = [f_departure.var for f_departure in departures
                                 if k_m <= f_arrival.date.nightsBetween(f_departure.date) <= k_M]
        sum_compatible_departures = Sum([If(var, 1, 0) for var in compatible_departures])
        # solver.add(Or(f_arrival.var == 0, sum_compatible_departures == 1))
        solver.add(If(f_arrival.var, 1, 0) <= sum_compatible_departures)
        solver.add(1 >= sum_compatible_departures)

    for f_departure in departures:
        compatible_arrivals = [f_arrival.var for f_arrival in arrivals
                               if k_m <= f_arrival.date.nightsBetween(f_departure.date) <= k_M]
        sum_compatible_arrivals = Sum([If(var, 1, 0) for var in compatible_arrivals])
        # solver.add(Or(f_departure.var == 0, sum_compatible_arrivals == 1))
        solver.add(If(f_departure.var, 1, 0) <= sum_compatible_arrivals)
        solver.add(1 >= sum_compatible_arrivals)
##### end: FOR EACH CITY, ARRIVAL AND DEPARTURE ARE k NIGHTS APART #####


##### SOLVING #####
if solver.check() == sat:
    model = solver.model()
    selected_vars = [str(var) for var in model if model[var]]
    selected_flights = [f for f in flights if f.var_name in selected_vars]
    total_cost = sum(f.cost for f in selected_flights)

    print(total_cost)
    for f in selected_flights:
        print(f)
##### end: SOLVING #####
