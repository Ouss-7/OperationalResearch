import tkinter as tk
from tkinter import simpledialog
import customtkinter as ctk
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk
import networkx as nx
import matplotlib.pyplot as plt
import random
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import string
import numpy as np
from collections import defaultdict

class Tache:
    def __init__(self, nom, duree):
        self.nom = nom
        self.duree = duree
        self.predecesseurs = []
        self.successeurs = []
        self.date_tot = 0  # Date au plus tôt
        self.date_tard = 0  # Date au plus tard
        self.marge_totale = 0
        self.marge_libre = 0

class Projet:
    def __init__(self):
        self.taches = {}
        self.debut = None
        self.fin = None
    
    def ajouter_tache(self, nom, duree):
        tache = Tache(nom, duree)
        self.taches[nom] = tache
        return tache
    
    def ajouter_contrainte(self, pred_nom, succ_nom):
        pred = self.taches[pred_nom]
        succ = self.taches[succ_nom]
        pred.successeurs.append(succ)
        succ.predecesseurs.append(pred)
    
    def calculer_dates_tot(self):
        sans_pred = [t for t in self.taches.values() if not t.predecesseurs]
        for tache in sans_pred:
            tache.date_tot = 0
        taches_traitees = set(sans_pred)
        while taches_traitees:
            tache = taches_traitees.pop()
            for succ in tache.successeurs:
                nouvelle_date = tache.date_tot + tache.duree
                succ.date_tot = max(succ.date_tot, nouvelle_date)
                if all(pred in taches_traitees or pred.date_tot is not None 
                      for pred in succ.predecesseurs):
                    taches_traitees.add(succ)
    
    def calculer_dates_tard(self):
        date_fin = max(t.date_tot + t.duree for t in self.taches.values())
        sans_succ = [t for t in self.taches.values() if not t.successeurs]
        for tache in sans_succ:
            tache.date_tard = date_fin - tache.duree
        taches_traitees = set(sans_succ)
        while taches_traitees:
            tache = taches_traitees.pop()
            for pred in tache.predecesseurs:
                nouvelle_date = tache.date_tard - pred.duree
                if pred.date_tard == 0 or nouvelle_date < pred.date_tard:
                    pred.date_tard = nouvelle_date
                if all(succ in taches_traitees or succ.date_tard is not None 
                      for succ in pred.successeurs):
                    taches_traitees.add(pred)
    
    def calculer_marges(self):
        for tache in self.taches.values():
            tache.marge_totale = tache.date_tard - tache.date_tot
            if tache.successeurs:
                date_min_succ = min(succ.date_tot for succ in tache.successeurs)
                tache.marge_libre = date_min_succ - (tache.date_tot + tache.duree)
            else:
                tache.marge_libre = tache.marge_totale
    
    def chemin_critique(self):
        return [t.nom for t in self.taches.values() if t.marge_totale == 0]

    def visualiser(self):
        G = nx.DiGraph()
        for nom, tache in self.taches.items():
            G.add_node(nom, duree=tache.duree,
                      tot=tache.date_tot,
                      tard=tache.date_tard,
                      marge=tache.marge_totale)
        for nom, tache in self.taches.items():
            for succ in tache.successeurs:
                G.add_edge(nom, succ.nom)
        
        pos = nx.spring_layout(G, k=1, iterations=50)
        plt.figure(figsize=(12, 8))
        nx.draw_networkx_edges(G, pos, edge_color='black', arrows=True)
        
        chemin_crit = self.chemin_critique()
        edges_crit = [(u, v) for (u, v) in G.edges() 
                     if u in chemin_crit and v in chemin_crit]
        nx.draw_networkx_edges(G, pos, edgelist=edges_crit, 
                             edge_color='red', arrows=True)
        
        node_colors = ['red' if node in chemin_crit else 'lightblue' 
                      for node in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                             node_size=1000)
        
        labels = {}
        for node in G.nodes():
            tache = self.taches[node]
            labels[node] = f"{node}\n{tache.duree}\n{tache.date_tot}/{tache.date_tard}"
        nx.draw_networkx_labels(G, pos, labels)
        
        plt.title("Graphe PERT/MPM avec chemin critique")
        plt.axis('off')
        plt.tight_layout()
        plt.show()

class ModernButton(ctk.CTkButton):
    def __init__(self, parent, text, icon, command=None):
        super().__init__(
            parent,
            text="",  # Remove text from button itself
            font=("Roboto", 14),
            corner_radius=10,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            text_color="white",
            compound="left",
            command=command,
            width=950,  # Fixed width for all buttons
            height=150  # Fixed height for all buttons
        )
        self.configure(image=ctk.CTkImage(Image.new("RGBA", (30, 30), (0, 0, 0, 0))))
        self.icon_label = ctk.CTkLabel(self, text=icon, font=("Segoe UI Emoji", 24), text_color="white")
        self.icon_label.place(relx=0.5, rely=0.3, anchor="center")  # Centered horizontally, placed at 30% from top
        
        # Add text label below icon
        self.text_label = ctk.CTkLabel(self, text=text, font=("Roboto", 14, "bold"), text_color="white")
        self.text_label.place(relx=0.5, rely=0.7, anchor="center")  # Centered horizontally, placed at 70% from top

class ModernOperationsResearchGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Algorithmes de Recherche Opérationnelle")
        self.root.geometry("1200x800")
        
        # Load the EMSI logo
        try:
            self.logo_image = Image.open("Capture.PNG")
            self.logo_image = self.logo_image.resize((150, 75))  # Adjust size as needed
            self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        except Exception as e:
            print(f"Could not load logo: {e}")
            self.logo_photo = None
        
        # Set theme colors
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Initialize frames for both pages
        self.main_page = ctk.CTkFrame(self.root, fg_color="white")
        self.algorithms_page = ctk.CTkFrame(self.root, fg_color="white")
        
        self.create_main_page()
        self.create_algorithms_page()
        
        # Show main page first
        self.show_main_page()

    def create_main_page(self):
        # Header
        header_frame = ctk.CTkFrame(self.main_page, corner_radius=0, fg_color="white")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Create a frame for names in left corner
        names_frame = ctk.CTkFrame(header_frame, fg_color="white")
        names_frame.pack(side="left", padx=20, pady=(10, 0))
        
        # Add names
        name_label = ctk.CTkLabel(
            names_frame,
            text="OSSAMA TIJANI",
            font=("Roboto", 10, "bold"),
            text_color="#120101"
        )
        name_label.pack(anchor="w")
        
        name_label2 = ctk.CTkLabel(
            names_frame,
            text="Dr. EL MKHALET Mouna",
            font=("Roboto", 10, "bold"),
            text_color="#120101"
        )
        name_label2.pack(anchor="w")
        
        # Add logo if available on the right
        if self.logo_photo:
            logo_label = tk.Label(header_frame, image=self.logo_photo, bg="white")
            logo_label.pack(side="right", padx=20, pady=(10, 0))

        
        title = ctk.CTkLabel(
            header_frame,
            text="Algorithmes de Recherche Opérationnelle ",
            font=("Roboto", 28, "bold"),
            text_color="#1e293b"
        )
        title.pack(pady=(20, 5))
        
        
        # Main content
        content_frame = ctk.CTkFrame(self.main_page, fg_color="white")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        algorithms_button = ModernButton(
            content_frame,
            text="Algorithmes",
            icon="🔍",
            command=self.show_algorithms_page
        )
        algorithms_button.pack(fill="x", padx=10, pady=5)
        
        # Footer
        self.create_footer(self.main_page)

    def create_algorithms_page(self):
        # Header
        header_frame = ctk.CTkFrame(self.algorithms_page, corner_radius=0, fg_color="white")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Create a frame for names in left corner
        names_frame = ctk.CTkFrame(header_frame, fg_color="white")
        names_frame.pack(side="left", padx=20, pady=(10, 0))
        
        # Add names
        name_label = ctk.CTkLabel(
            names_frame,
            text="OSSAMA TIJANI",
            font=("Roboto", 10, "bold"),
            text_color="#120101"
        )
        name_label.pack(anchor="w")
        
        name_label2 = ctk.CTkLabel(
            names_frame,
            text="Dr. EL MKHALET Mouna",
            font=("Roboto", 10, "bold"),
            text_color="#120101"
        )
        name_label2.pack(anchor="w")
        
        # Add logo if available on the right
        if self.logo_photo:
            logo_label = tk.Label(header_frame, image=self.logo_photo, bg="white")
            logo_label.pack(side="right", padx=20, pady=(10, 0))

        title = ctk.CTkLabel(
            header_frame,
            text="Algorithmes de Recherche Opérationnelle ",
            font=("Roboto", 28, "bold"),
            text_color="#1e293b"
        )
        title.pack(pady=(20, 5))
        
      
        
        # Create a frame for the scrollable content
        content_frame = ctk.CTkFrame(self.algorithms_page, fg_color="white")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add scrollbar
        scrollbar = ctk.CTkScrollbar(content_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Create canvas for scrolling
        canvas = tk.Canvas(content_frame, bg="white", yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        
        # Configure scrollbar
        scrollbar.configure(command=canvas.yview)
        
        # Create frame for buttons inside canvas
        buttons_frame = ctk.CTkFrame(canvas, fg_color="white")
        
        # Add buttons frame to canvas
        canvas.create_window((0, 0), window=buttons_frame, anchor="nw")
        
        # Define algorithms with their icons
        algorithms = [
            ("Welsh-Powell : Minimiser le nombre de couleurs nécessaires pour colorer un graphe sans conflits entre sommets adjacents.", "⚡", self.run_welsh_powell),
            ("Dijkstra : Trouver le chemin le plus court et le moins coûteux entre deux points dans un graphe pondéré.", "🔍", self.run_dijkstra),
            ("Kruskal : Construire un arbre couvrant minimal avec le poids total des arêtes le plus faible.", "🌳", self.run_kruskal),
            ("Moindre Coût : Minimiser les coûts de transport tout en respectant l'offre et la demande.", "📊", self.moindre_cout_callback),
            ("Nord-Ouest : Fournir une solution initiale simple pour les problèmes de transport.", "🧭", self.nord_ouest_callback),
            ("Stepping-Stone : Optimiser une solution de transport en réduisant les coûts.", "🔄", self.stepping_stone_callback),
            ("Bellman-Ford : Calculer les chemins les plus courts, même avec des poids négatifs, depuis une source unique.", "📈", self.bellman_ford_callback),
            ("Ford-Fulkerson : Maximiser le flot possible dans un réseau entre une source et un puits.", "🔀", self.ford_fulkerson_callback),
            ("Potentiel Metra : Planifier et optimiser les tâches d’un projet en identifiant les chemins critiques.", "⚖️", self.potentiel_metra_callback)
        ]
        
        # Create buttons
        for algo, icon, command in algorithms:
            btn = ModernButton(
                buttons_frame,
                text=algo,
                icon=icon,
                command=command
            )
            btn.pack(fill="x", padx=10, pady=5)
        
        # Update scroll region when buttons frame changes

        def update_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        buttons_frame.bind("<Configure>", update_scroll_region)
        
        # Configure canvas scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Footer
        self.create_footer(self.algorithms_page, show_back_button=True)

    def create_footer(self, parent, show_back_button=False):
        footer_frame = ctk.CTkFrame(parent, corner_radius=0, fg_color="white")
        footer_frame.pack(fill="x", side="bottom")
        
        quit_button = ctk.CTkButton(
            footer_frame,
            text="Quitter",
            font=("Roboto", 14),
            fg_color="#ef4444",
            hover_color="#dc2626",
            corner_radius=10,
            command=self.quit_application
        )
        quit_button.pack(side="right", padx=(0, 20), pady=20)

        if show_back_button:
            back_button = ctk.CTkButton(
                footer_frame,
                text="Retour",
                font=("Roboto", 14),
                fg_color="#64748b",
                hover_color="#475569",
                corner_radius=10,
                command=self.show_main_page
            )
            back_button.pack(side="right", padx=20, pady=20)


    def show_main_page(self):
        self.algorithms_page.pack_forget()
        self.main_page.pack(fill="both", expand=True)

    def show_algorithms_page(self):
        self.main_page.pack_forget()
        self.algorithms_page.pack(fill="both", expand=True)

    def show_algorithm_info(self, algorithm):
        info = f"Information sur l'algorithme : {algorithm}\n\nCette fonctionnalité est en cours de développement."
        messagebox.showinfo("Information sur l'algorithme", info)

    def potentiel_metra_callback(self):
        try:
            # Create new project
            projet = Projet()
            
            # Ask for number of tasks
            n = simpledialog.askinteger("Input", "Entrez le nombre de tâches :", parent=self.root, minvalue=2)
            if n is None:  # User cancelled
                return

            # Get task information
            for i in range(n):
                task_name = simpledialog.askstring("Input", f"Nom de la tâche {i+1}:", parent=self.root)
                if task_name is None:  # User cancelled
                    return
                    
                duration = simpledialog.askinteger("Input", f"Durée de la tâche {task_name}:", parent=self.root, minvalue=0)
                if duration is None:  # User cancelled
                    return
                    
                projet.ajouter_tache(task_name, duration)

            # Get dependencies
            while True:
                if not messagebox.askyesno("Question", "Voulez-vous ajouter une contrainte de précédence?"):
                    break
                    
                pred = simpledialog.askstring("Input", 
                    f"Tâche prédécesseur ({', '.join(projet.taches.keys())}):", 
                    parent=self.root)
                if pred not in projet.taches:
                    messagebox.showerror("Error", "Tâche invalide")
                    continue
                    
                succ = simpledialog.askstring("Input", 
                    f"Tâche successeur ({', '.join(projet.taches.keys())}):", 
                    parent=self.root)
                if succ not in projet.taches:
                    messagebox.showerror("Error", "Tâche invalide")
                    continue
                    
                projet.ajouter_contrainte(pred, succ)

            # Calculate dates and margins
            projet.calculer_dates_tot()
            projet.calculer_dates_tard()
            projet.calculer_marges()
            
            # Display results
            result_text = "Résultats du calcul PERT/MPM:\n\n"
            for nom, tache in projet.taches.items():
                result_text += f"Tâche {nom}:\n"
                result_text += f"  Durée: {tache.duree}\n"
                result_text += f"  Date au plus tôt: {tache.date_tot}\n"
                result_text += f"  Date au plus tard: {tache.date_tard}\n"
                result_text += f"  Marge totale: {tache.marge_totale}\n"
                result_text += f"  Marge libre: {tache.marge_libre}\n\n"
            
            result_text += f"Chemin critique: {' -> '.join(projet.chemin_critique())}"
            
            # Show results and visualize
            messagebox.showinfo("Résultats Potentiel Metra", result_text)
            projet.visualiser()
                
        except Exception as e:
            messagebox.showerror("Error", f"Une erreur s'est produite: {str(e)}")

    def quit_application(self):
        if messagebox.askokcancel("Quitter", "Voulez-vous quitter l'application?"):
            self.root.destroy()

    def run(self):
        self.root.mainloop()

    # Methods copied from OperationsResearchGUI
    def print_graph_to_console(self, G):
        print(f"Nombre de sommets : {G.number_of_nodes()}")
        print(f"Nombre d'arêtes : {G.number_of_edges()}")
        print("Liste des arêtes :")
        for edge in G.edges():
            print(str(edge))  # Ensure edges are printed as strings
            
    def run_dijkstra(self):
        try:
            # Prompt user for number of vertices
            n = simpledialog.askinteger("Input", "Entrez le nombre de sommets pour le graphe :", parent=self.root, minvalue=1)
            if n is None:  # User cancelled
                return
            
            # Generate the random graph
            G = self.generer_graphe_aleatoire(n)
            
            # Prompt user for start and end nodes
            depart = simpledialog.askstring("Input", 
                f"Entrez le sommet de départ ({', '.join(G.nodes)}) :", 
                parent=self.root)
            
            if depart not in G.nodes:
                messagebox.showerror("Error", "Le sommet de départ n'est pas valide.")
                return
            
            arrivee = simpledialog.askstring("Input", 
                f"Entrez le sommet d'arrivée ({', '.join(G.nodes)}) :", 
                parent=self.root)
            
            if arrivee not in G.nodes:
                messagebox.showerror("Error", "Le sommet d'arrivée n'est pas valide.")
                return
            
            # Calculate shortest path
            try:
                chemin = nx.dijkstra_path(G, depart, arrivee, weight='weight')
                distance_totale = nx.dijkstra_path_length(G, depart, arrivee, weight='weight')
                
                # Display results
                result_text = f"Le plus court chemin entre {depart} et {arrivee} est : {' -> '.join(chemin)}\nDistance totale : {distance_totale}\n"
                messagebox.showinfo("Résultats de Dijkstra", result_text)
                
                # Visualize the graph with the shortest path
                self.visualize_dijkstra(G, depart, arrivee, chemin)
                
            except nx.NetworkXNoPath:
                messagebox.showerror("Error", 
                    f"Aucun chemin entre {depart} et {arrivee}.")
            except Exception as e:
                messagebox.showerror("Error", 
                    f"Une erreur s'est produite: {str(e)}")
        
        except Exception as e:
            messagebox.showerror("Error", 
                f"Une erreur s'est produite: {str(e)}")
    def run_welsh_powell(self):
        try:
            # Prompt user for number of vertices
            n = simpledialog.askinteger("Input", "Entrez le nombre de sommets pour le graphe :", parent=self.root, minvalue=1)
            if n is None:  # User cancelled
                return
            
            # Generate a random graph
            G = nx.Graph()
            G.add_nodes_from(range(n))  # Add n nodes
            
            # Add edges with 50% probability
            for i in range(n):
                for j in range(i + 1, n):
                    if random.random() > 0.5:
                        G.add_edge(i, j)

            # Welsh Powell algorithm
            colors = self.welsh_powell_coloring(G)
            self.visualize_graph(G, colors)

        except Exception as e:
            messagebox.showerror("Error", f"Une erreur s'est produite: {str(e)}")

    def welsh_powell_coloring(self, G):
        sorted_nodes = sorted(G.nodes(), key=lambda x: G.degree(x), reverse=True)
        node_colors = {}
        for node in sorted_nodes:
            neighbor_colors = {node_colors[neighbor] for neighbor in G.neighbors(node) if neighbor in node_colors}
            color = 0
            while color in neighbor_colors:
                color += 1
            node_colors[node] = color
        return node_colors

    def visualize_graph(self, G, colors):
        color_map = [colors[node] for node in G.nodes()]
        
        plt.clf()  # Clear any existing plots
        nx.draw(G, with_labels=True, node_color=color_map, edge_color='gray', node_size=700, font_size=10)
        plt.title("Welsh Powell Graph Coloring")
        plt.show()

    def visualize_dijkstra(self, G, start_node, end_node, path):
        plt.clf()  # Clear any existing plots
        pos = nx.spring_layout(G)
        
        # Draw the basic graph
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=500)
        nx.draw_networkx_edges(G, pos, edge_color='gray')
        nx.draw_networkx_labels(G, pos)
        
        # Draw edge labels
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        
        # Highlight the path
        path_edges = list(zip(path[:-1], path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='r', width=2)
        
        # Highlight start and end nodes
        nx.draw_networkx_nodes(G, pos, nodelist=[start_node], node_color='g', node_size=500)
        nx.draw_networkx_nodes(G, pos, nodelist=[end_node], node_color='r', node_size=500)
        
        plt.title("Visualisation du plus court chemin (Dijkstra)")
        plt.axis('off')
        plt.show()


    def run_kruskal(self):
        try:
            n = simpledialog.askinteger("Input", "Entrez le nombre de sommets pour le graphe :", parent=self.root, minvalue=2)
            if n is None:  # User cancelled
                return
            
            G = self.generer_graphe_aleatoire(n)
            mst, cout_mst = self.calculer_mst_kruskal(G)

            result_text = f"Le coût de l'arbre de minimum spanning tree : {cout_mst}\n"
            messagebox.showinfo("Résultats de Kruskal", result_text)
            self.dessiner_graphe_et_mst(G, mst)

        except Exception as e:
            messagebox.showerror("Error", f"Une erreur s'est produite: {str(e)}")

    def generer_noms_sommets(self, n):
        alphabet = list(string.ascii_uppercase)
        if n <= 26:
            return alphabet[:n]
        else:
            noms_double_lettre = [a + b for a in alphabet for b in alphabet]
            return alphabet + noms_double_lettre[:n - 26]

    def generer_graphe_aleatoire(self, n):
        G = nx.Graph()
        sommets = self.generer_noms_sommets(n)
        for i in range(n):
            for j in range(i + 1, n):
                poids = random.randint(1, 100)
                G.add_edge(sommets[i], sommets[j], weight=poids)
        return G

    def calculer_mst_kruskal(self, G):
        mst = nx.Graph()
        arretes_tries = sorted(G.edges(data=True), key=lambda x: x[2]['weight'])
        parent = {i: i for i in G.nodes()}

        def trouver_parent(noeud):
            if parent[noeud] == noeud:
                return noeud
            return trouver_parent(parent[noeud])

        def fusionner_ensembles(u, v):
            racine_u = trouver_parent(u)
            racine_v = trouver_parent(v)
            parent[racine_u] = racine_v

        cout_mst = 0
        for u, v, data in arretes_tries:
            if trouver_parent(u) != trouver_parent(v):
                mst.add_edge(u, v, weight=data['weight'])
                cout_mst += data['weight']
                fusionner_ensembles(u, v)

        return mst, cout_mst

    def dessiner_graphe_et_mst(self, G, mst):
        pos = nx.spring_layout(G)
        etiquettes_arretes = nx.get_edge_attributes(G, 'weight')

        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=etiquettes_arretes)

        arretes_mst = list(mst.edges())
        nx.draw_networkx_edges(G, pos, edgelist=arretes_mst, edge_color='r', width=2)

        plt.title("Graphe et Arbre de Minimum Spanning Tree")
        plt.show()

    def generate_random_data(self, num_magazines, num_usines):
        # Generate random transportation costs, factory capacities, and store demands
        couts_transport = np.random.randint(1, 100, size=(num_magazines, num_usines)).tolist()
        capacites_usines = np.random.randint(50, 200, size=num_usines).tolist()
        demandes_magazines = np.random.randint(30, 100, size=num_magazines).tolist()
        return couts_transport, capacites_usines, demandes_magazines

    def algorithme_moindre_cout(self, capacites_usines, demandes_magazines, couts_transport):
        # Implement the "Moindre Coût" algorithm here
        # This is a placeholder for the actual implementation
        allocation = np.zeros((len(demandes_magazines), len(capacites_usines))).tolist()
        # Example allocation logic (to be replaced with actual algorithm)
        for i in range(len(demandes_magazines)):
            for j in range(len(capacites_usines)):
                allocation[i][j] = min(demandes_magazines[i], capacites_usines[j])
                demandes_magazines[i] -= allocation[i][j]
                capacites_usines[j] -= allocation[i][j]
        return allocation

    def algorithme_nord_ouest(self, capacites_usines, demandes_magazines, couts_transport):
        # Implement the "Nord-Ouest" algorithm here
        # This is a placeholder for the actual implementation
        allocation = np.zeros((len(demandes_magazines), len(capacites_usines))).tolist()
        # Example allocation logic (to be replaced with actual algorithm)
        for i in range(len(demandes_magazines)):
            for j in range(len(capacites_usines)):
                allocation[i][j] = min(demandes_magazines[i], capacites_usines[j])
                demandes_magazines[i] -= allocation[i][j]
                capacites_usines[j] -= allocation[i][j]
        return allocation

    def algorithme_stepping_stone(self, allocation, couts_transport):
        # Implement the "Stepping Stone" algorithm here
        # This is a placeholder for the actual implementation
        return allocation  # Return the same allocation for now

    def moindre_cout_callback(self):
        num_magazines = simpledialog.askinteger("Input", "Nombre de magasins :")
        num_usines = simpledialog.askinteger("Input", "Nombre d'usines :")
        
        couts_transport, capacites_usines, demandes_magazines = self.generate_random_data(num_magazines, num_usines)
        
        allocation = self.algorithme_moindre_cout(capacites_usines.copy(), demandes_magazines.copy(), couts_transport)
        cout_total = self.calculer_cout_total(allocation, couts_transport)
        
        result_text = f"Coût total : {cout_total}\nAllocation :\n{allocation}"
        messagebox.showinfo("Résultats de Moindre Coût", result_text)

    def nord_ouest_callback(self):
        num_magazines = simpledialog.askinteger("Input", "Nombre de magasins :")
        num_usines = simpledialog.askinteger("Input", "Nombre d'usines :")
        
        couts_transport, capacites_usines, demandes_magazines = self.generate_random_data(num_magazines, num_usines)
        
        allocation = self.algorithme_nord_ouest(capacites_usines.copy(), demandes_magazines.copy(), couts_transport)
        cout_total = self.calculer_cout_total(allocation, couts_transport)
        
        result_text = f"Coût total : {cout_total}\nAllocation :\n{allocation}"
        messagebox.showinfo("Résultats de Nord-Ouest", result_text)

    def stepping_stone_callback(self):
        num_magazines = simpledialog.askinteger("Input", "Nombre de magasins :")
        num_usines = simpledialog.askinteger("Input", "Nombre d'usines :")
        
        couts_transport, capacites_usines, demandes_magazines = self.generate_random_data(num_magazines, num_usines)
        
        initial_allocation = self.algorithme_nord_ouest(capacites_usines.copy(), demandes_magazines.copy(), couts_transport)
        optimized_allocation = self.algorithme_stepping_stone(initial_allocation, couts_transport)
        cout_total = self.calculer_cout_total(optimized_allocation, couts_transport)
        
        result_text = f"Coût total après optimisation : {cout_total}\nAllocation optimisée :\n{optimized_allocation}"
        messagebox.showinfo("Résultats de Stepping-Stone", result_text)

    def calculer_cout_total(self, allocation, couts_transport):
        # Calculate the total transportation cost based on the allocation and costs
        total_cost = 0
        for i in range(len(allocation)):
            for j in range(len(allocation[i])):
                total_cost += allocation[i][j] * couts_transport[i][j]
        return total_cost

    def bellman_ford_callback(self):
        try:
            n = simpledialog.askinteger("Input", "Entrez le nombre de sommets pour le graphe :", parent=self.root, minvalue=2)
            if n is None:  # User cancelled
                return
            
            G = self.generer_graphe_aleatoire(n)
            start_node = simpledialog.askstring("Input", "Entrez le sommet de départ (ex: A, B, C, ...):", parent=self.root)
            
            if start_node not in G.nodes:
                messagebox.showerror("Error", "Le sommet de départ n'est pas valide.")
                return
            
            distances, predecessors = self.bellman_ford(G, start_node)

            result_text = f"Distances depuis le sommet {start_node}:\n"
            for node, distance in distances.items():
                result_text += f"{node}: {distance}\n"

            messagebox.showinfo("Résultats de Bellman-Ford", result_text)
            self.visualize_bellman_ford(G, distances, start_node)

        except Exception as e:
            messagebox.showerror("Error", f"Une erreur s'est produite: {str(e)}")

    def bellman_ford(self, G, start_node):
        # Initialize distances and predecessors
        distances = {node: float('inf') for node in G.nodes()}
        distances[start_node] = 0
        predecessors = {node: None for node in G.nodes()}

        # Relax edges up to |V| - 1 times
        for _ in range(len(G.nodes()) - 1):
            for u, v, data in G.edges(data=True):
                weight = data['weight']
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    predecessors[v] = u

        # Check for negative-weight cycles
        for u, v, data in G.edges(data=True):
            weight = data['weight']
            if distances[u] + weight < distances[v]:
                raise ValueError("Le graphe contient un cycle de poids négatif.")

        return distances, predecessors

    def visualize_bellman_ford(self, G, distances, start_node):
        pos = nx.spring_layout(G)
        edge_labels = nx.get_edge_attributes(G, 'weight')

        # Draw the graph
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        # Highlight the shortest paths
        for node, distance in distances.items():
            if distance < float('inf'):
                nx.draw_networkx_nodes(G, pos, nodelist=[node], node_color='green' if node != start_node else 'yellow')

        plt.title("Visualisation de l'algorithme de Bellman-Ford")
        plt.show()

    def visualize_ford_fulkerson(self, graph, source, sink, max_flow):
        """Visualizes the Ford-Fulkerson flow network."""
        plt.clf()  # Clear any existing plots
        
        # Create a NetworkX graph for visualization
        G = nx.DiGraph()
        
        # Add all vertices
        for v in range(graph.V):
            G.add_node(v)
        
        # Add edges with their capacities and flows
        for u in range(graph.V):
            for v in graph.graph[u]:
                capacity = graph.capacity.get((u, v), 0)
                flow = max(0, graph.capacity.get((v, u), 0))  # Reverse edge capacity represents the flow
                if capacity > 0:
                    G.add_edge(u, v, capacity=capacity, flow=flow)
        
        pos = nx.spring_layout(G)
        
        # Draw the basic graph
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=500)
        nx.draw_networkx_labels(G, pos)
        
        # Draw edges with different colors based on flow/capacity
        edge_colors = []
        edge_widths = []
        edge_labels = {}
        
        for u, v, data in G.edges(data=True):
            capacity = data['capacity']
            flow = data['flow']
            
            # Create edge label showing flow/capacity
            edge_labels[(u, v)] = f'{flow}/{capacity}'
            
            # Color edges based on flow percentage
            if flow == 0:
                edge_colors.append('gray')
                edge_widths.append(1)
            elif flow == capacity:
                edge_colors.append('red')
                edge_widths.append(2)
            else:
                edge_colors.append('blue')
                edge_widths.append(1.5)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        
        # Highlight source and sink nodes
        nx.draw_networkx_nodes(G, pos, nodelist=[source], node_color='g', node_size=500)
        nx.draw_networkx_nodes(G, pos, nodelist=[sink], node_color='r', node_size=500)
        
        plt.title(f"Visualisation de Ford-Fulkerson (Flot Maximum: {max_flow})")
        plt.axis('off')
        plt.show()

    def ford_fulkerson_callback(self):
        try:
            num_vertices = simpledialog.askinteger("Input", "Entrez le nombre de sommets :", parent=self.root, minvalue=2)
            if num_vertices is None:  # User cancelled
                return
            
            g = Graph(num_vertices)

            # Generate random edges with capacities
            for _ in range(num_vertices * 2):  # Randomly create edges
                u = random.randint(0, num_vertices - 1)
                v = random.randint(0, num_vertices - 1)
                if u != v:  # Avoid self-loops
                    capacity = random.randint(1, 20)  # Random capacity between 1 and 20
                    g.add_edge(u, v, capacity)

            source = simpledialog.askinteger("Input", "Entrez le sommet source :", parent=self.root, minvalue=0, maxvalue=num_vertices - 1)
            sink = simpledialog.askinteger("Input", "Entrez le sommet puits :", parent=self.root, minvalue=0, maxvalue=num_vertices - 1)

            if source == sink:
                messagebox.showerror("Error", "Le sommet source et le sommet puits ne peuvent pas être identiques.")
                return

            max_flow = g.ford_fulkerson(source, sink)
            min_cut_edges = g.min_cut(source)

            result_text = f"Le flot maximum est : {max_flow}\nCoupe minimale : {min_cut_edges}"
            messagebox.showinfo("Résultats de Ford-Fulkerson", result_text)
            
            # Add visualization
            self.visualize_ford_fulkerson(g, source, sink, max_flow)

        except Exception as e:
            messagebox.showerror("Error", f"Une erreur s'est produite: {str(e)}")

class Graph:
    def __init__(self, vertices):
        self.graph = defaultdict(list)  # Dictionary to store the graph
        self.V = vertices                 # Number of vertices in the graph
        self.capacity = {}                # Dictionary to store capacities

    def add_edge(self, u, v, capacity):
        """Adds an edge (u -> v) with a given capacity."""
        self.graph[u].append(v)
        self.graph[v].append(u)  # Add the reverse edge for the residual graph
        self.capacity[(u, v)] = capacity
        self.capacity[(v, u)] = 0  # Initial reverse capacity (for the residual graph)

    def _dfs(self, source, visited):
        """Depth-first search (DFS) to mark reachable vertices from the source."""
        visited[source] = True
        for neighbor in self.graph[source]:
            if not visited[neighbor] and self.capacity[(source, neighbor)] > 0:
                self._dfs(neighbor, visited)

    def ford_fulkerson(self, source, sink):
        """Implements the Ford-Fulkerson algorithm to calculate the maximum flow."""
        parent = [-1] * self.V
        max_flow = 0

        while True:
            visited = [False] * self.V
            if not self._dfs_find_path(source, sink, visited, parent):
                break

            # Find the minimum capacity in the augmenting path
            path_flow = float('inf')
            s = sink
            while s != source:
                path_flow = min(path_flow, self.capacity[(parent[s], s)])
                s = parent[s]

            # Update residual capacities
            v = sink
            while v != source:
                u = parent[v]
                self.capacity[(u, v)] -= path_flow
                self.capacity[(v, u)] += path_flow
                v = parent[v]

            max_flow += path_flow

        return max_flow

    def _dfs_find_path(self, source, sink, visited, parent):
        """Finds an augmenting path using DFS."""
        visited[source] = True
        if source == sink:
            return True
        for neighbor in self.graph[source]:
            if not visited[neighbor] and self.capacity[(source, neighbor)] > 0:
                parent[neighbor] = source
                if self._dfs_find_path(neighbor, sink, visited, parent):
                    return True
        return False

    def min_cut(self, source):
        """Finds and displays the edges of the minimum cut after running Ford-Fulkerson."""
        visited = [False] * self.V
        self._dfs(source, visited)

        min_cut_edges = []
        for u in range(self.V):
            for v in self.graph[u]:
                if visited[u] and not visited[v] and self.capacity[(u, v)] == 0:
                    min_cut_edges.append((u, v))

        return min_cut_edges

if __name__ == "__main__":
    app = ModernOperationsResearchGUI()
    app.root.mainloop()