import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import itertools

st.set_page_config(page_title="Tourist Travel Planner", layout="wide", page_icon="🗺️")

st.title("🗺️ Tourist Travel Planner")
st.markdown("Find the most efficient route across your selected cities based on the distances you provide. This uses an exact permutation solver, making it ideal for up to 10 cities.")

# Initialize a default dataframe
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "Source": ["A", "B", "C", "A", "A", "B", "C"],
        "Destination": ["B", "C", "A", "C", "D", "D", "D"],
        "Distance": [10.0, 15.0, 20.0, 12.0, 30.0, 25.0, 10.0]
    })

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Edit Travel Distances")
    st.markdown("Add or edit edges between cities. Distance must be numeric.")
    edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with col2:
    st.subheader("Calculate Optimal Route")
    
    if st.button("Solve TSP", type="primary"):
        # Validate data
        df = edited_df.dropna()
        try:
            df["Distance"] = pd.to_numeric(df["Distance"])
        except ValueError:
            st.error("Distance column must contain only numeric values.")
            st.stop()
            
        nodes = set(df["Source"].unique()) | set(df["Destination"].unique())
        
        if len(nodes) < 3:
            st.warning("Please input at least 3 distinct cities.")
            st.stop()
            
        if len(nodes) > 10:
            st.warning("For performance reasons, the exact solver is limited to 10 distinct cities.")
            st.stop()
            
        # Create an undirected graph
        G = nx.Graph()
        for idx, row in df.iterrows():
            G.add_edge(row["Source"], row["Destination"], weight=row["Distance"])
            
        # Brute-force exact TSP evaluation
        node_list = list(nodes)
        min_cost = float('inf')
        best_path = None
        
        # By fixing the start node, we reduce permutations by a factor of N
        start_node = node_list[0]
        other_nodes = node_list[1:]
        
        has_solution = False
        
        # Add a progress bar to show processing
        progress_text = "Computing optimal route..."
        my_bar = st.progress(0, text=progress_text)
        
        perms = list(itertools.permutations(other_nodes))
        total_perms = len(perms)
        
        for i, p in enumerate(perms):
            if i % max(1, total_perms // 10) == 0:
                 my_bar.progress(i / total_perms, text=progress_text)
                 
            current_path = [start_node] + list(p) + [start_node]
            
            # Evaluate path cost
            valid = True
            cost = 0
            for j in range(len(current_path) - 1):
                u = current_path[j]
                v = current_path[j+1]
                if G.has_edge(u, v):
                    cost += G[u][v].get('weight', float('inf'))
                else:
                    valid = False
                    break
            
            if valid and cost < min_cost:
                min_cost = cost
                best_path = current_path
                has_solution = True
                
        my_bar.empty()
                
        if not has_solution:
            st.error("No valid route exists visiting all cities with the given connections. Ensure all your cities are interconnected!")
        else:
            st.success(f"Optimal Route Found! Total Distance: **{min_cost}**")
            
            # Format the route string
            route_str = " ➔ ".join(str(path_node) for path_node in best_path)
            st.info(f"**Path**: {route_str}")
            
            # Visualize the graph
            fig, ax = plt.subplots(figsize=(8, 6))
            pos = nx.spring_layout(G, seed=42)
            
            # Draw nodes and basic network labels
            nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=700, ax=ax)
            nx.draw_networkx_labels(G, pos, font_size=12, font_family='sans-serif', font_weight='bold', ax=ax)
            
            # Draw standard edges
            edge_labels = nx.get_edge_attributes(G, 'weight')
            nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.3)
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax, font_color='gray')
            
            # Highlight the optimal route edges
            route_edges = [(best_path[k], best_path[k+1]) for k in range(len(best_path)-1)]
            nx.draw_networkx_edges(G, pos, edgelist=route_edges, edge_color='red', width=3.0, alpha=0.8, ax=ax)
            
            ax.set_title("City Network (Optimal Route highlighted in Red)")
            ax.axis('off')
            st.pyplot(fig)
