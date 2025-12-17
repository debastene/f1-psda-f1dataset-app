import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS (STYLING)
# ==========================================
st.set_page_config(page_title="F1 Race Analytics", layout="wide", page_icon="🏎️")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #1f2937; padding: 10px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; background-color: #374151; border-radius: 5px; color: white; border: none; padding: 0 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #ef4444 !important; }
    div[data-testid="stMetricValue"] { color: #10b981; }
    .stTable { background-color: #1f2937; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. ALGORITMA MANUAL (POKOK BAHASAN PSDA)
# ==========================================

# [Sort - Quick Sort]

def quick_sort(data, key):
    if len(data) <= 1: return data
    pivot = data[len(data) // 2][key]
    left = [x for x in data if x[key] > pivot]
    middle = [x for x in data if x[key] == pivot]
    right = [x for x in data if x[key] < pivot]
    return quick_sort(left, key) + middle + quick_sort(right, key)

# [Search - Binary Search]
def binary_search(data, target_name):
    low, high = 0, len(data) - 1
    target_name = target_name.lower()
    while low <= high:
        mid = (low + high) // 2
        if target_name in data[mid]['name'].lower(): return data[mid]
        elif data[mid]['name'].lower() < target_name: low = mid + 1
        else: high = mid - 1
    return None

# [Recursion]
def recursive_sum_points(arr):
    if not arr: return 0
    return arr[0] + recursive_sum_points(arr[1:])

def factorial(n):
    if n <= 1: return 1
    return n * factorial(n - 1)

# [Tree - BST]

class Node:
    def __init__(self, data):
        self.data, self.left, self.right = data, None, None

class BST:
    def __init__(self): self.root = None
    def insert(self, data):
        if not self.root: self.root = Node(data)
        else: self._ins(self.root, data)
    def _ins(self, node, data):
        if data['points'] < node.data['points']:
            if not node.left: node.left = Node(data)
            else: self._ins(node.left, data)
        else:
            if not node.right: node.right = Node(data)
            else: self._ins(node.right, data)
    def inorder(self, node, res):
        if node:
            self.inorder(node.left, res)
            res.append(node.data)
            self.inorder(node.right, res)

# ==========================================
# 3. DATA LOADER & SESSION STATE
# ==========================================
if 'history' not in st.session_state: st.session_state.history = []
if 'manual_data' not in st.session_state: st.session_state.manual_data = []

@st.cache_data
def load_data():
    def find_f(name):
        for path in [os.path.join('archive (1)', name), name]:
            if os.path.exists(path): return path
        return None
    res_p, drv_p = find_f('results.csv'), find_f('drivers.csv')
    if res_p and drv_p:
        try:
            r_df = pd.read_csv(res_p, encoding='unicode_escape')
            d_df = pd.read_csv(drv_p, encoding='unicode_escape')
            df = pd.merge(r_df, d_df, on='driverId')
            df['name'] = df['forename'] + " " + df['surname']
            return df[['driverId', 'name', 'points', 'grid', 'laps']].drop_duplicates('name').to_dict('records')
        except: return []
    return []

# ==========================================
# 4. MAIN DASHBOARD UI
# ==========================================

st.markdown("<h1 style='text-align: center; color: #ef4444;'>🏎️ F1 Race Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #9ca3af;'>Penerapan Struktur Data & Algoritma pada Data Formula 1</p>", unsafe_allow_html=True)

data = load_data()

if not data:
    st.error("Dataset tidak ditemukan. Pastikan folder 'archive (1)' ada.")
else:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Sort Algorithms", "🔍 Search & Hash", "🌳 Tree Structure", "🔄 Recursive", "📥 Input Data"])

    with tab1:
        st.subheader("Sorting Algorithms Comparison")
        col1, col2, col3 = st.columns(3)
        with col1: sort_algo = st.selectbox("Algorithm", ["Quick Sort", "Bubble Sort"])
        with col2: sort_metric = st.selectbox("Sort By", ["points", "laps", "grid"])
        
        start_t = time.time()
        sample_data = data[:100]
        if sort_algo == "Quick Sort": sorted_data = quick_sort(sample_data, sort_metric)
        else:
            sorted_data = sample_data.copy()
            for i in range(len(sorted_data)):
                for j in range(0, len(sorted_data)-i-1):
                    if sorted_data[j][sort_metric] < sorted_data[j+1][sort_metric]:
                        sorted_data[j], sorted_data[j+1] = sorted_data[j+1], sorted_data[j]
        
        exec_time = (time.time() - start_t) * 1000
        with col3: st.metric("Execution Time", f"{exec_time:.4f} ms")

        chart_df = pd.DataFrame(sorted_data).head(10)
        fig = px.bar(chart_df, x='name', y=sort_metric, color_discrete_sequence=['#ef4444'])
        fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.table(chart_df[['name', 'points', 'laps', 'grid']])

    with tab2:
        st.subheader("Search & Hashing")
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1: search_query = st.text_input("Enter Driver Name", placeholder="e.g. Hamilton")
        with col_s2: search_btn = st.button("Search Driver")
        
        if search_btn and search_query:
            sorted_name = sorted(data, key=lambda x: x['name'])
            res = binary_search(sorted_name, search_query)
            if res: st.success(f"Driver Found: {res['name']}"); st.json(res)
            else: st.error("Driver not found.")

        st.divider()
        st.subheader("Hash Table Visualization")
        hash_size = 10
        hash_table = [[] for _ in range(hash_size)]
        for d in data[:20]:
            idx = len(d['name']) % hash_size
            hash_table[idx].append(d['name'].split()[-1])
        cols = st.columns(5)
        for i in range(hash_size):
            with cols[i % 5]:
                st.markdown(f"**Bucket {i}**")
                st.code("\n".join(hash_table[i]) if hash_table[i] else "Empty")

    with tab3:
        st.subheader("Binary Search Tree - Rankings")
        bst = BST()
        for d in data[:15]: bst.insert(d)
        tree_res = []
        bst.inorder(bst.root, tree_res)
        st.write("Inorder Traversal (Sorted):")
        st.dataframe(pd.DataFrame(tree_res[::-1]), use_container_width=True)

    with tab4:
        st.subheader("Recursive Algorithms")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            n_fact = st.number_input("Input N for Factorial", 1, 20, 5)
            if st.button("Calculate Factorial"): st.write(f"Result: {factorial(n_fact)}")
        with col_r2:
            if st.button("Calculate Total Points (Recursive)"):
                total_pts = recursive_sum_points([d['points'] for d in data[:50]])
                st.write(f"Total: {total_pts}")

    with tab5:
        st.subheader("Manual Data Entry (Stack & Queue Implementation)")
        
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1: input_name = st.text_input("Driver Name")
        with c2: input_time = st.text_input("Lap Time (e.g. 1:30.5)")
        with c3: mode = st.radio("Mode", ["Stack", "Queue"])
        
        if st.button("Add Driver"):
            if input_name and input_time:
                new_entry = {"name": input_name, "laptime": input_time, "timestamp": time.strftime("%H:%M:%S")}
                if mode == "Stack":
                    st.session_state.manual_data.insert(0, new_entry) # LIFO
                else:
                    st.session_state.manual_data.append(new_entry) # FIFO
                st.toast(f"Added via {mode}!")
            else: st.warning("Please fill both fields.")

        st.divider()
        st.write(f"Current List (Total: {len(st.session_state.manual_data)})")
        if st.session_state.manual_data:
            st.table(pd.DataFrame(st.session_state.manual_data))
            if st.button("Pull Data (Remove First/Top Item)"):
                removed = st.session_state.manual_data.pop(0)
                st.info(f"Pulled: {removed['name']}")
                st.rerun()
        else: st.info("List is empty.")

st.sidebar.title("🕒 Activity Log")
if st.button("Clear Log"): st.session_state.history = []
for log in reversed(st.session_state.history[-10:]):
    st.sidebar.write(f"• {log}")
