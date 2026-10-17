import json
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "blockchain_data.json"

STAGES = ["Manufacturer", "Distributor", "Retailer", "Customer"]


def now_text():
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def calculate_hash(block):
    """Create a SHA-256 hash from the block's contents, excluding its own hash."""
    payload = {
        "index": block["index"],
        "timestamp": block["timestamp"],
        "transaction": block["transaction"],
        "previous_hash": block["previous_hash"],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class SupplyChainBlockchain:
    """A small educational blockchain stored locally as JSON."""

    def __init__(self):
        self.blocks = []
        self.load()

    def create_genesis_block(self):
        block = {
            "index": 0,
            "timestamp": now_text(),
            "transaction": {
                "type": "GENESIS",
                "product_id": "-",
                "product_name": "Supply Chain Tracking",
                "stage": "System",
                "location": "Local demo",
                "handled_by": "System",
                "notes": "First block in this demonstration blockchain.",
            },
            "previous_hash": "0",
        }
        block["hash"] = calculate_hash(block)
        return block

    def load(self):
        if DATA_FILE.exists():
            try:
                with DATA_FILE.open("r", encoding="utf-8") as file:
                    data = json.load(file)
                if isinstance(data, list) and data:
                    self.blocks = data
                    return
            except (json.JSONDecodeError, OSError):
                pass
        self.blocks = [self.create_genesis_block()]
        self.save()

    def save(self):
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(self.blocks, file, indent=2, ensure_ascii=False)

    def add_transaction(self, transaction):
        previous = self.blocks[-1]
        block = {
            "index": len(self.blocks),
            "timestamp": now_text(),
            "transaction": transaction,
            "previous_hash": previous["hash"],
        }
        block["hash"] = calculate_hash(block)
        self.blocks.append(block)
        self.save()
        return block

    def verify(self):
        if not self.blocks:
            return False, "The blockchain is empty."
        for i, block in enumerate(self.blocks):
            if block.get("hash") != calculate_hash(block):
                return False, f"Block {i} has been changed: its hash does not match."
            expected_previous = "0" if i == 0 else self.blocks[i - 1].get("hash")
            if block.get("previous_hash") != expected_previous:
                return False, f"Block {i} is not correctly linked to the previous block."
            if block.get("index") != i:
                return False, f"Block index mismatch at position {i}."
        return True, f"All {len(self.blocks)} blocks passed the integrity check."

    def product_transactions(self, product_id):
        return [
            b for b in self.blocks
            if b.get("transaction", {}).get("product_id", "").lower() == product_id.lower()
        ]

    def latest_stage(self, product_id):
        records = self.product_transactions(product_id)
        if not records:
            return None
        return records[-1]["transaction"].get("stage")


class SupplyChainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Supply Chain Tracking")
        self.geometry("1120x740")
        self.minsize(900, 620)
        self.blockchain = SupplyChainBlockchain()
        self.configure(bg="#f3f6fb")
        self.setup_style()
        self.build_ui()
        self.refresh_all()

    def setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#f3f6fb")
        style.configure("Card.TFrame", background="white")
        style.configure("TLabel", background="#f3f6fb", foreground="#1f2937", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground="#14213d", background="#f3f6fb")
        style.configure("Sub.TLabel", font=("Segoe UI", 10), foreground="#526174", background="#f3f6fb")
        style.configure("CardTitle.TLabel", font=("Segoe UI", 12, "bold"), foreground="#14213d", background="white")
        style.configure("TButton", font=("Segoe UI", 10), padding=7)
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=27)
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def build_ui(self):
        header = ttk.Frame(self, padding=(20, 16, 20, 8))
        header.pack(fill="x")
        ttk.Label(header, text="Supply Chain Tracking", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="A simple blockchain demo: record each product hand-off and verify its history.",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(3, 0))

        self.stats_var = tk.StringVar()
        ttk.Label(header, textvariable=self.stats_var, font=("Segoe UI", 10, "bold")).pack(anchor="e", pady=(0, 4))

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(4, 16))

        self.register_tab = ttk.Frame(self.tabs, padding=16)
        self.update_tab = ttk.Frame(self.tabs, padding=16)
        self.history_tab = ttk.Frame(self.tabs, padding=16)
        self.chain_tab = ttk.Frame(self.tabs, padding=16)
        self.tabs.add(self.register_tab, text="  Register Product  ")
        self.tabs.add(self.update_tab, text="  Update Journey  ")
        self.tabs.add(self.history_tab, text="  Product History  ")
        self.tabs.add(self.chain_tab, text="  Blockchain Explorer  ")

        self.build_register_tab()
        self.build_update_tab()
        self.build_history_tab()
        self.build_chain_tab()

    def make_card(self, parent, title):
        card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w", pady=(0, 12))
        return card

    def build_register_tab(self):
        card = self.make_card(self.register_tab, "Register a new product")
        card.pack(fill="x", anchor="n")
        self.reg_id = tk.StringVar()
        self.reg_name = tk.StringVar()
        self.reg_location = tk.StringVar()
        self.reg_handler = tk.StringVar()
        fields = [
            ("Product ID", self.reg_id, "e.g. PROD-001"),
            ("Product name", self.reg_name, "e.g. Organic Cotton T-shirt"),
            ("Manufacturer location", self.reg_location, "e.g. Ahmedabad, Gujarat"),
            ("Handled by", self.reg_handler, "e.g. ABC Manufacturing"),
        ]
        for label, variable, placeholder in fields:
            row = ttk.Frame(card, style="Card.TFrame")
            row.pack(fill="x", pady=5)
            ttk.Label(row, text=label, width=23, background="white").pack(side="left")
            ttk.Entry(row, textvariable=variable).pack(side="left", fill="x", expand=True, ipady=4)
        ttk.Label(
            card,
            text="Registration creates the first product transaction at the Manufacturer stage.",
            background="white",
            foreground="#526174",
        ).pack(anchor="w", pady=(10, 12))
        ttk.Button(card, text="Register Product", style="Accent.TButton", command=self.register_product).pack(anchor="w")
        ttk.Label(
            self.register_tab,
            text="Tip: Use a unique Product ID for every item or batch you want to track.",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=12)

    def build_update_tab(self):
        card = self.make_card(self.update_tab, "Record the next hand-off")
        card.pack(fill="x", anchor="n")
        self.up_id = tk.StringVar()
        self.up_location = tk.StringVar()
        self.up_handler = tk.StringVar()
        self.up_notes = tk.StringVar()
        row = ttk.Frame(card, style="Card.TFrame")
        row.pack(fill="x", pady=5)
        ttk.Label(row, text="Product ID", width=23, background="white").pack(side="left")
        self.product_combo = ttk.Combobox(row, textvariable=self.up_id, state="normal")
        self.product_combo.pack(side="left", fill="x", expand=True, ipady=4)
        self.current_stage_var = tk.StringVar(value="Current stage: —")
        ttk.Label(card, textvariable=self.current_stage_var, background="white", foreground="#235789").pack(anchor="w", pady=6)
        for label, variable, placeholder in [
            ("New stage location", self.up_location, "e.g. Distribution centre, Surat"),
            ("Handled by", self.up_handler, "e.g. XYZ Logistics"),
            ("Notes (optional)", self.up_notes, "e.g. Package received in good condition"),
        ]:
            row = ttk.Frame(card, style="Card.TFrame")
            row.pack(fill="x", pady=5)
            ttk.Label(row, text=label, width=23, background="white").pack(side="left")
            ttk.Entry(row, textvariable=variable).pack(side="left", fill="x", expand=True, ipady=4)
        ttk.Button(card, text="Add Next Stage to Blockchain", style="Accent.TButton", command=self.add_stage).pack(anchor="w", pady=(12, 0))
        ttk.Label(
            self.update_tab,
            text="Allowed order: Manufacturer → Distributor → Retailer → Customer. Each hand-off adds a new block.",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=12)
        self.product_combo.bind("<<ComboboxSelected>>", lambda _event: self.update_current_stage())

    def build_history_tab(self):
        top = ttk.Frame(self.history_tab)
        top.pack(fill="x", pady=(0, 10))
        ttk.Label(top, text="Product ID:").pack(side="left")
        self.history_id = tk.StringVar()
        ttk.Entry(top, textvariable=self.history_id, width=25).pack(side="left", padx=8)
        ttk.Button(top, text="View History", command=self.show_history).pack(side="left")
        ttk.Button(top, text="Show All Products", command=self.show_all_history).pack(side="left", padx=8)

        columns = ("block", "time", "stage", "location", "handler", "notes")
        self.history_tree = ttk.Treeview(self.history_tab, columns=columns, show="headings", height=17)
        headings = {"block": "Block", "time": "Timestamp", "stage": "Stage", "location": "Location",
                    "handler": "Handled by", "notes": "Notes"}
        widths = {"block": 60, "time": 155, "stage": 115, "location": 170, "handler": 150, "notes": 260}
        for col in columns:
            self.history_tree.heading(col, text=headings[col])
            self.history_tree.column(col, width=widths[col], anchor="w")
        self.history_tree.pack(fill="both", expand=True)
        self.history_tree.tag_configure("odd", background="#f2f6fc")
        self.history_status = tk.StringVar(value="Enter a Product ID to view its traceability history.")
        ttk.Label(self.history_tab, textvariable=self.history_status, style="Sub.TLabel").pack(anchor="w", pady=(8, 0))

    def build_chain_tab(self):
        top = ttk.Frame(self.chain_tab)
        top.pack(fill="x", pady=(0, 10))
        ttk.Button(top, text="Verify Blockchain Integrity", style="Accent.TButton", command=self.verify_chain).pack(side="left")
        ttk.Button(top, text="Refresh Blocks", command=self.refresh_chain_tree).pack(side="left", padx=8)
        self.verify_var = tk.StringVar(value="Integrity status has not been checked yet.")
        ttk.Label(top, textvariable=self.verify_var, foreground="#235789").pack(side="left", padx=12)

        columns = ("index", "time", "product", "stage", "previous", "hash")
        self.chain_tree = ttk.Treeview(self.chain_tab, columns=columns, show="headings", height=17)
        headings = {"index": "Block #", "time": "Timestamp", "product": "Product ID", "stage": "Stage",
                    "previous": "Previous hash", "hash": "Block hash"}
        widths = {"index": 65, "time": 155, "product": 115, "stage": 115, "previous": 250, "hash": 250}
        for col in columns:
            self.chain_tree.heading(col, text=headings[col])
            self.chain_tree.column(col, width=widths[col], anchor="w")
        self.chain_tree.pack(fill="both", expand=True)
        self.chain_tree.tag_configure("odd", background="#f2f6fc")
        ttk.Label(
            self.chain_tab,
            text="SHA-256 hashes link each block to the previous block. This is an educational local demo, not a distributed production blockchain.",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(8, 0))

    def known_product_ids(self):
        ids = []
        for block in self.blockchain.blocks:
            tx = block.get("transaction", {})
            pid = tx.get("product_id", "")
            if pid and pid != "-" and pid not in ids:
                ids.append(pid)
        return ids

    def register_product(self):
        product_id = self.reg_id.get().strip()
        product_name = self.reg_name.get().strip()
        location = self.reg_location.get().strip()
        handler = self.reg_handler.get().strip()
        if not all([product_id, product_name, location, handler]):
            messagebox.showwarning("Missing information", "Please fill in all four fields.")
            return
        if product_id.lower() in [p.lower() for p in self.known_product_ids()]:
            messagebox.showerror("Product ID already exists", "Please use a unique Product ID.")
            return
        tx = {
            "type": "PRODUCT_STAGE",
            "product_id": product_id,
            "product_name": product_name,
            "stage": "Manufacturer",
            "location": location,
            "handled_by": handler,
            "notes": "Product registered in the supply chain.",
        }
        self.blockchain.add_transaction(tx)
        self.reg_id.set("")
        self.reg_name.set("")
        self.reg_location.set("")
        self.reg_handler.set("")
        self.refresh_all()
        self.up_id.set(product_id)
        self.history_id.set(product_id)
        self.show_history()
        messagebox.showinfo("Product registered", f"{product_name} has been added to the blockchain.")

    def update_current_stage(self):
        pid = self.up_id.get().strip()
        stage = self.blockchain.latest_stage(pid) if pid else None
        self.current_stage_var.set(f"Current stage: {stage or 'Product not found'}")

    def add_stage(self):
        product_id = self.up_id.get().strip()
        location = self.up_location.get().strip()
        handler = self.up_handler.get().strip()
        notes = self.up_notes.get().strip()
        if not product_id:
            messagebox.showwarning("Missing Product ID", "Select or enter a Product ID.")
            return
        records = self.blockchain.product_transactions(product_id)
        if not records:
            messagebox.showerror("Product not found", "Register this Product ID first.")
            return
        current_stage = records[-1]["transaction"]["stage"]
        if current_stage == "Customer":
            messagebox.showinfo("Journey complete", "This product has already reached the Customer stage.")
            return
        next_stage = STAGES[STAGES.index(current_stage) + 1]
        if not location or not handler:
            messagebox.showwarning("Missing information", "Please enter the new location and handled-by name.")
            return
        original_name = records[0]["transaction"].get("product_name", product_id)
        tx = {
            "type": "PRODUCT_STAGE",
            "product_id": product_id,
            "product_name": original_name,
            "stage": next_stage,
            "location": location,
            "handled_by": handler,
            "notes": notes or f"Product received at {next_stage} stage.",
        }
        self.blockchain.add_transaction(tx)
        self.up_location.set("")
        self.up_handler.set("")
        self.up_notes.set("")
        self.refresh_all()
        self.up_id.set(product_id)
        self.update_current_stage()
        self.history_id.set(product_id)
        self.show_history()
        messagebox.showinfo("Stage recorded", f"{product_id} moved to {next_stage}.")

    def show_history(self):
        pid = self.history_id.get().strip()
        if not pid:
            messagebox.showwarning("Product ID required", "Enter a Product ID first.")
            return
        blocks = self.blockchain.product_transactions(pid)
        self.clear_tree(self.history_tree)
        for n, block in enumerate(blocks):
            tx = block["transaction"]
            self.history_tree.insert("", "end", values=(
                block["index"], block["timestamp"], tx.get("stage", ""),
                tx.get("location", ""), tx.get("handled_by", ""), tx.get("notes", "")
            ), tags=("odd",) if n % 2 else ())
        if blocks:
            name = blocks[0]["transaction"].get("product_name", pid)
            self.history_status.set(f"{name} — {len(blocks)} recorded stage(s). Latest stage: {blocks[-1]['transaction'].get('stage', '')}.")
        else:
            self.history_status.set(f"No product history found for Product ID '{pid}'.")

    def show_all_history(self):
        self.clear_tree(self.history_tree)
        records = [b for b in self.blockchain.blocks if b.get("transaction", {}).get("product_id") not in ("", "-")]
        for n, block in enumerate(records):
            tx = block["transaction"]
            self.history_tree.insert("", "end", values=(
                block["index"], block["timestamp"], tx.get("stage", ""),
                tx.get("location", ""), tx.get("handled_by", ""), tx.get("notes", "")
            ), tags=("odd",) if n % 2 else ())
        self.history_status.set(f"Showing all {len(records)} product stage transaction(s).")

    @staticmethod
    def clear_tree(tree):
        for item in tree.get_children():
            tree.delete(item)

    def refresh_chain_tree(self):
        self.clear_tree(self.chain_tree)
        for n, block in enumerate(self.blockchain.blocks):
            tx = block.get("transaction", {})
            self.chain_tree.insert("", "end", values=(
                block.get("index", ""), block.get("timestamp", ""),
                tx.get("product_id", ""), tx.get("stage", ""),
                block.get("previous_hash", "")[:20] + "...",
                block.get("hash", "")[:20] + "...",
            ), tags=("odd",) if n % 2 else ())
        self.stats_var.set(f"Blocks: {len(self.blockchain.blocks)}  |  Products: {len(self.known_product_ids())}")

    def verify_chain(self):
        valid, message = self.blockchain.verify()
        self.verify_var.set(("✓ " if valid else "✗ ") + message)
        if valid:
            messagebox.showinfo("Blockchain verified", message)
        else:
            messagebox.showerror("Integrity check failed", message)

    def refresh_all(self):
        ids = self.known_product_ids()
        self.product_combo["values"] = ids
        if self.up_id.get().strip() not in ids:
            self.up_id.set(ids[-1] if ids else "")
        self.update_current_stage()
        self.refresh_chain_tree()


if __name__ == "__main__":
    app = SupplyChainApp()
    app.mainloop()
