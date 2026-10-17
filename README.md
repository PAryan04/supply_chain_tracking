# Supply Chain Tracking — Blockchain Demo

A simple Python GUI project for a college Blockchain subject. It demonstrates how a product's journey can be recorded as linked blocks.

## Features
- Register a product at the Manufacturer stage.
- Move it through Distributor, Retailer, and Customer.
- View a product's full traceability history.
- Explore blocks and their previous/current hashes.
- Verify block hashes and links to detect accidental/tampered data changes.
- Save data locally in `blockchain_data.json`.

## Technology
- Python 3
- Tkinter (desktop GUI)
- JSON (local persistence)
- SHA-256 hashing (`hashlib`)

No third-party Python packages are required. Tkinter is included with most standard Windows Python installations.

## How to run on Windows
1. Extract the project ZIP to a folder.
2. Double-click `supply_chain_tracking.pyw` to open the desktop GUI without a console window.
3. If double-clicking does not work, right-click the file and choose **Open with** your Python installation.
4. The first launch creates `blockchain_data.json` in the same folder. Keep this file to retain your records.

You can also open the file in VS Code and use **Run Python File**, although that may show a terminal in VS Code.

## Suggested demonstration
1. Register `PROD-001`, name `Organic Cotton T-shirt`, manufacturer location `Ahmedabad`, handled by `ABC Manufacturing`.
2. Open **Update Journey**, select `PROD-001`, enter a distributor location and handler, and add the next stage.
3. Repeat for Retailer and Customer.
4. Open **Product History** to show the journey.
5. Open **Blockchain Explorer** and click **Verify Blockchain Integrity**.

## How the blockchain works in this project
Each stage is stored as a transaction inside a block. A block contains an index, timestamp, transaction details, previous block hash, and its own SHA-256 hash. The next block stores the previous block's hash, creating a chain. If stored block data is changed, the hash verification should fail.

## Project limitations
This is an educational simulation, not a production blockchain. It runs on one computer, has no peer-to-peer network or consensus mechanism, and the JSON file can be edited by someone with access to the computer. Hashes make changes detectable when verified; they do not by themselves prevent someone from rewriting the entire local file and recalculating hashes.
