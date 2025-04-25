import tkinter as tk
from core import WeCareSystem
from pathlib import Path
import logging

logging.basicConfig(filename='wecare.log', level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    Path("D:/skincare/receipts").mkdir(exist_ok=True)
    Path("D:/skincare/stock_alerts").mkdir(exist_ok=True)
    root = tk.Tk()
    wecare = WeCareSystem(root)
    wecare.run()