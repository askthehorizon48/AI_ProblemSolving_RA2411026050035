import streamlit as st
from z3 import *

st.set_page_config(page_title="Wumpus World Inference Engine", layout="wide", page_icon="🦇")

st.title("🦇 Wumpus World Inference Engine")
st.markdown("Interact with the grid to input your observations (Visited, Breeze, Stench). The Z3 Theorem Prover will instantly deduce which cells are mathematically guaranteed to be **Safe**, contain a **Pit**, contain the **Wumpus**, or remain **Risky**.")

N = 4

# Initialize session state for grid
if "grid" not in st.session_state:
    st.session_state.grid = {}
    for r in range(N):
        for c in range(N):
            st.session_state.grid[(r, c)] = {"visited": False, "breeze": False, "stench": False}
    # Starting cell (0,0) is visited by default
    st.session_state.grid[(0,0)]["visited"] = True

def get_adjacent(r, c):
    adj = []
    if r > 0: adj.append((r-1, c))
    if r < N-1: adj.append((r+1, c))
    if c > 0: adj.append((r, c-1))
    if c < N-1: adj.append((r, c+1))
    return adj

# Define Z3 Boolean variables for Pits and Wumpuses
P_vars = { (r,c): Bool(f"P_{r}_{c}") for r in range(N) for c in range(N) }
W_vars = { (r,c): Bool(f"W_{r}_{c}") for r in range(N) for c in range(N) }

def get_base_solver():
    """Constructs the base Z3 solver with axioms and current observable facts."""
    s = Solver()
    
    # Rule 1: Starting point (0,0) has no pit and no wumpus
    s.add(Not(P_vars[(0,0)]))
    s.add(Not(W_vars[(0,0)]))
    
    # Rule 2: There is exactly one Wumpus in the cavern
    wumpus_list = [W_vars[(r,c)] for r in range(N) for c in range(N)]
    s.add(Or(*wumpus_list)) # At least one
    for i in range(len(wumpus_list)):
        for j in range(i+1, len(wumpus_list)):
             s.add(Or(Not(wumpus_list[i]), Not(wumpus_list[j]))) # At most one
             
    # Incorporate current observable facts
    for r in range(N):
        for c in range(N):
            cell = st.session_state.grid[(r,c)]
            if cell["visited"]:
                # If we visited it and didn't die, it's safe right now
                s.add(Not(P_vars[(r,c)]))
                s.add(Not(W_vars[(r,c)]))
                
                # Axiom: Breeze iff Pit in an adjacent cell
                adj_pits = [P_vars[adj] for adj in get_adjacent(r,c)]
                if cell["breeze"]:
                    s.add(Or(*adj_pits))
                else:
                    for adj in get_adjacent(r,c):
                        s.add(Not(P_vars[adj]))
                        
                # Axiom: Stench iff Wumpus in an adjacent cell
                adj_wumps = [W_vars[adj] for adj in get_adjacent(r,c)]
                if cell["stench"]:
                    s.add(Or(*adj_wumps))
                else:
                    for adj in get_adjacent(r,c):
                        s.add(Not(W_vars[adj]))
                        
    return s

def query_entailment(solver, statement):
    """
    Returns True if the statement is logically entailed by the solver's axioms.
    We prove this by showing that 'Not(statement)' is unsatisfiable.
    """
    solver.push()
    solver.add(Not(statement))
    result = solver.check()
    solver.pop()
    
    return result == unsat

# Step 1: Initialize the solver
base_solver = get_base_solver()

# Validate if the current state is logically contradictory (e.g. user input impossible states)
is_contradiction = False
if base_solver.check() == unsat:
    is_contradiction = True

# Step 2: Evaluate board state via Z3
board_status = {}
for r in range(N):
    for c in range(N):
        if is_contradiction:
             board_status[(r,c)] = "Contradiction!"
             continue
             
        if st.session_state.grid[(r,c)]["visited"]:
            board_status[(r,c)] = "✔️ Visited"
        else:
            # Check safely entailed states
            safe = query_entailment(base_solver, And(Not(P_vars[(r,c)]), Not(W_vars[(r,c)])))
            pit = query_entailment(base_solver, P_vars[(r,c)])
            wumpus = query_entailment(base_solver, W_vars[(r,c)])
            
            if pit and wumpus:
                board_status[(r,c)] = "💀 Pit & Wumpus!"
            elif pit:
                board_status[(r,c)] = "🕳️ Guaranteed Pit!"
            elif wumpus:
                board_status[(r,c)] = "🦇 Guaranteed Wumpus!"
            elif safe:
                board_status[(r,c)] = "🛡️ 100% Safe"
            else:
                board_status[(r,c)] = "❓ Unknown / Risky"

if is_contradiction:
    st.error("⚠️ The current observations result in a logical contradiction! Please check your markings.")

st.markdown("---")

# Step 3: Draw Streamlit UI
# We render row by row
for r in range(N):
    cols = st.columns(4)
    for c in range(N):
        with cols[c]:
            cell_state = st.session_state.grid[(r,c)]
            status = board_status[(r,c)]
            
            # Choose border color based on status
            if "Visited" in status:
                border_color = "#28a745" # green
                bg_color = "rgba(40, 167, 69, 0.1)"
            elif "Safe" in status:
                border_color = "#17a2b8" # lightblue
                bg_color = "rgba(23, 162, 184, 0.1)"
            elif "Pit" in status or "Wumpus" in status:
                border_color = "#dc3545" # red
                bg_color = "rgba(220, 53, 69, 0.1)"
            else:
                border_color = "#6c757d" # gray
                bg_color = "rgba(108, 117, 125, 0.1)"
                
            # Render a styled container visually acting like a room
            st.markdown(
                f"""
                <div style="border: 2px solid {border_color}; background-color: {bg_color}; border-radius: 8px; padding: 15px; margin-bottom: 5px; text-align: center; height: 110px;">
                    <h4 style="margin: 0; padding: 0;">({r}, {c})</h4>
                    <p style="margin-top: 5px; font-weight: bold;">{status}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Form to edit cell state underneath the container
            with st.expander(f"Edit ({r},{c})"):
                visited = st.checkbox("Visited", value=cell_state["visited"], key=f"v_{r}_{c}")
                breeze = st.checkbox("Breeze", value=cell_state["breeze"], key=f"b_{r}_{c}", disabled=not visited)
                stench = st.checkbox("Stench", value=cell_state["stench"], key=f"s_{r}_{c}", disabled=not visited)
                
                if st.button("Update Cell", key=f"btn_{r}_{c}"):
                    st.session_state.grid[(r,c)]["visited"] = visited
                    
                    # Ensure unvisited cells clear their observations
                    if not visited:
                         st.session_state.grid[(r,c)]["breeze"] = False
                         st.session_state.grid[(r,c)]["stench"] = False
                    else:
                         st.session_state.grid[(r,c)]["breeze"] = breeze
                         st.session_state.grid[(r,c)]["stench"] = stench
                         
                    st.rerun()

st.markdown("---")
st.markdown("**Instructions**: Start at cell (0,0). When your agent moves into a safe cell, expand its 'Edit' menu and check 'Visited'. If your agent senses a Breeze or Stench in that room, check those boxes and hit 'Update Cell'. The Grid will dynamically recalculate inferences for all unvisited adjacent (and board-wide) rooms instantly.")
