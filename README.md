# AI Problem Solving Assignment
**Register Number:** RA2411026050035  
**Author:** Aadi Sasikumar

## 🚀 Project Overview
This repository contains implementations for two Artificial Intelligence problem-solving tasks as part of the AI coursework. The solutions focus on optimization and logical inference using Python.

---

## 📍 Problem 7: Tourist Travel Planner (TSP)

### Description
A tourist needs to visit a set of destinations in the shortest possible time and return to the starting point. This system allows the user to input destinations and distances through a GUI to find the most efficient route.

### Algorithm: Traveling Salesman Problem (TSP)
* **Approach:** Implements the TSP approach to minimize total travel distance.
* **Constraints:** Each location is visited exactly once, and the journey must return to the start.
* **Logic:** Uses a search-based optimization to evaluate path costs and return the optimal sequence.

### Execution Steps
1. Navigate to the `Tourist_Travel_Planner/` directory.
2. Run `pip install -r requirements.txt`.
3. Execute `python main.py`.
4. Enter the city names and their respective distances in the interactive GUI.
5. Click "Find Optimal Route" to view the results.

---

## 🕵️ Problem 15: Wumpus World Decision System

### Description
A logic-based inference agent designed to navigate a hazardous environment. The agent must avoid pits and the Wumpus by analyzing environmental percepts like "Breeze" and "Stench" provided by the user.

### Algorithm: Logical Inference / Rule-Based Reasoning
* **Model:** Based on the Wumpus World Model using Propositional Logic.
* **Percepts:**
    * **Breeze:** Indicates a Pit is in an adjacent cell.
    * **Stench:** Indicates the Wumpus is in an adjacent cell.
* **Inference:** The system applies rules to mark cells as "Safe," "Unsafe," or "Possible Danger" to suggest a safe path.

### Execution Steps
1. Navigate to the `Wumpus_World/` directory.
2. Run `python wumpus_gui.py`.
3. Use the interactive grid to input percepts (Breeze/Stench) for specific cells.
4. The system will dynamically display the inferred safe cells and the recommended path.

---

